import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DEBUG = int(os.environ.get("DEBUG", default=0))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
LOGIN = os.environ.get('DJ_ADMIN_USERNAME')
PASSWORD = os.environ.get('DJ_ADMIN_PASSWORD')

if DEBUG:
    # URL = "http://127.0.0.1:8000/"
    URL = "http://localhost:8000/"
else:
    URL = os.environ.get("MY_HOST")
