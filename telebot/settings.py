import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# BOT_TOKEN = os.environ['BOT_TOKEN']
# USERNAME = os.environ['DJ_ADMIN_USERNAME']
# PASSWORD = os.environ['DJ_ADMIN_PASSWORD']

BOT_TOKEN = os.environ.get('BOT_TOKEN')
USERNAME = os.environ.get('DJ_ADMIN_USERNAME')
PASSWORD = os.environ.get('DJ_ADMIN_PASSWORD')
