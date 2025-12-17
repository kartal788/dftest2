import sys
import os
from unittest.mock import MagicMock
from datetime import timezone

sys.path.append(os.getcwd())

class MockPytz(MagicMock):
    def timezone(self, name):
        return timezone.utc

sys.modules['pytz'] = MockPytz()

MOCK_MODULES = [
    'bson', 'motor', 'motor.motor_asyncio', 'pyrogram', 'pyrogram.types', 
    'pyrogram.errors', 'pyrogram.file_id', 'pyrogram.session', 'pyrogram.raw', 
    'tgcrypto', 'pymongo', 'uvicorn', 'aiohttp', 'dotenv',
    'fastapi', 'fastapi.responses', 'fastapi.middleware', 
    'fastapi.middleware.cors', 'fastapi.staticfiles', 'fastapi.security',
    'starlette', 'starlette.middleware', 'starlette.middleware.sessions'
]

class MockModule(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        if name == "__path__": return []
        return MagicMock()

sys.modules.update((mod_name, MockModule()) for mod_name in MOCK_MODULES)

import types
db_module = types.ModuleType('Backend.helper.database')
db_module.Database = MagicMock()
sys.modules['Backend.helper.database'] = db_module

logger_module = types.ModuleType('Backend.logger')
logger_module.LOGGER = MagicMock()
sys.modules['Backend.logger'] = logger_module

try:
    print("Attempting to import Backend.fastapi.main...")
    import Backend.fastapi.main
    if hasattr(Backend.fastapi.main, 'app'):
        print("✅ Successfully imported Backend.fastapi.main and found 'app'")
    else:
        print("❌ Imported module but 'app' not found?")
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
