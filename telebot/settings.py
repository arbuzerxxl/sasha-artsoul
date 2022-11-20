import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DOCKER = int(os.environ.get("DEBUG", default=0))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
USERNAME = os.environ.get('DJ_ADMIN_USERNAME')
PASSWORD = os.environ.get('DJ_ADMIN_PASSWORD')

if DOCKER:
    URL = "http://main:8000/"
else:
    URL = "http://localhost:8000/"
