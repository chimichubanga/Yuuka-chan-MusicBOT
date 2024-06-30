from dotenv import load_dotenv
import os

# Загрузка переменных из файла .env
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
BOT_PREFIX = os.getenv('BOT_PREFIX')
OWNER_ID = os.getenv('OWNER_ID')
EMBEDCOLOR = int(os.getenv('EMBEDCOLOR', '0xF8AA2A'), 16)
BOT_ACTIVITY_TYPE = int(os.getenv('BOT_ACTIVITY_TYPE', 0))
BOT_ACTIVITY_NAME = os.getenv('BOT_ACTIVITY_NAME', '')
PLAYLIST_SONG_COUNT = int(os.getenv('PLAYLIST_SONG_COUNT', 0))
WELCOME_ROLE_ID = os.getenv('WELCOME_ROLE_ID')
