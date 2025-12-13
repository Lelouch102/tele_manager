# config.py

import os
from dotenv import load_dotenv
import json

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = set(map(int, os.getenv("ADMIN_IDS", "").split(',')))
EXPIRATION_TIME=28800

MONGO_URI=os.getenv("MONGO_URI")
DB_NAME=os.getenv("DB_NAME")

TELEGRAM_APPS = json.loads(os.getenv("TELEGRAM_APPS"))