import uvicorn
import logging
import copy
from Backend.config import Telegram
from Backend.fastapi.main import app

class ProtocolErrorFilter(logging.Filter):
    def filter(self, record):
        if record.exc_info:
            _, exc_value, _ = record.exc_info
            if "LocalProtocolError" in str(type(exc_value)) or "Too little data" in str(exc_value):
                return False
        return True

Port = Telegram.PORT

# Configure Logging to suppress ProtocolError
log_config = copy.deepcopy(uvicorn.config.LOGGING_CONFIG)

# 1. Add Filter Definition
log_config["filters"]["protocol_filter"] = {
    "()": "Backend.fastapi.ProtocolErrorFilter"
}

# 2. Add Filter to Handlers
# 'default' handler handles 'uvicorn.error'
if "default" in log_config["handlers"]:
    if "filters" not in log_config["handlers"]["default"]:
        log_config["handlers"]["default"]["filters"] = []
    log_config["handlers"]["default"]["filters"].append("protocol_filter")

# 'access' handler handles 'uvicorn.access' (Requests)
if "access" in log_config["handlers"]:
    if "filters" not in log_config["handlers"]["access"]:
        log_config["handlers"]["access"]["filters"] = []
    log_config["handlers"]["access"]["filters"].append("protocol_filter")

config = uvicorn.Config(app=app, host='0.0.0.0', port=Port, log_config=log_config)
server = uvicorn.Server(config)
