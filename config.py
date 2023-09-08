import os
from dotenv import load_dotenv

from filter import Filter

load_dotenv()

ETHERUM_NODE_WS_URI = os.getenv("ETHERUM_NODE_WS_URI")
TELEGRAM_BOT_API = os.getenv("TELEGRAM_BOT_API")
g_bot_is_running = False
g_uptime = 0
