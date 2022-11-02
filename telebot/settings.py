import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

BOT_TOKEN = os.environ.get('BOT_TOKEN')
USERNAME = os.environ.get('DJ_ADMIN_USERNAME')
PASSWORD = os.environ.get('DJ_ADMIN_PASSWORD')
URL = "http://main:8000/"
