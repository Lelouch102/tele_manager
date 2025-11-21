# config.py

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = set(map(int, os.getenv("ADMIN_IDS", "").split(',')))
EXPIRATION_TIME=28800

MONGO_URI=os.getenv("MONGO_URI")
DB_NAME=os.getenv("DB_NAME")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")