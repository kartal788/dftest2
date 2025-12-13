from asyncio import sleep
from pyrogram.errors import FloodWait, MessageDeleteForbidden
from Backend.logger import LOGGER
from Backend.pyrofork.bot import Helper, multi_clients
from itertools import cycle

async def edit_message(chat_id: int, msg_id: int, new_caption: str):
    try:
        await Helper.edit_message_caption(
            chat_id=chat_id,
            message_id=msg_id,
            caption=new_caption
        )
        await sleep(2)
    except FloodWait as e:
        LOGGER.warning(f"FloodWait for {e.value} seconds while editing message {msg_id} in {chat_id}")
        await sleep(e.value)
    except Exception as e:
        LOGGER.error(f"Error while editing message {msg_id} in {chat_id}: {e}")

_client_cycle = None

def get_next_client():
    global _client_cycle
    
    if _client_cycle is None:
        # Create a list of all available clients including Helper
        clients = [Helper]
        if multi_clients:
            clients.extend(multi_clients.values())
        
        # Remove duplicates if any (though multi_clients shouldn't have Helper inside typically)
        unique_clients = list({c.name: c for c in clients}.values())
        _client_cycle = cycle(unique_clients)
    
    try:
        return next(_client_cycle)
    except StopIteration:
        _client_cycle = cycle([Helper])
        return next(_client_cycle)


async def delete_message(chat_id: int, msg_id: int):
    # Determine max retries based on available clients
    # +1 for Helper, and loop through all multi_clients if needed
    max_retries = len(multi_clients) + 1 if multi_clients else 1
    failed_clients = []
    
    for _ in range(max_retries):
        client = get_next_client()
        try:
            await client.delete_messages(
                chat_id=chat_id,
                message_ids=msg_id
            )
            await sleep(2)
            if failed_clients:
                 LOGGER.info(f"Deleted message {msg_id} in {chat_id} using Client: {client.name} (Previous failures: {', '.join(failed_clients)})")
            else:
                 LOGGER.info(f"Deleted message {msg_id} in {chat_id} using Client: {client.name}")
            return # Success, exit loop
            
        except FloodWait as e:
            LOGGER.warning(f"FloodWait for {e.value} seconds while deleting message {msg_id} in {chat_id} using Client: {client.name}")
            await sleep(e.value)
            
        except MessageDeleteForbidden:
            failed_clients.append(client.name)
            continue # Try next client
            
        except Exception as e:
            LOGGER.error(f"Error while deleting message {msg_id} in {chat_id} using Client: {client.name}: {e}")
            break

    if failed_clients:
        LOGGER.error(f"Failed to delete message {msg_id} in {chat_id}. Permission denied for clients: [{', '.join(failed_clients)}]")
    else:
        LOGGER.error(f"Failed to delete message {msg_id} in {chat_id} after {max_retries} attempts.")
