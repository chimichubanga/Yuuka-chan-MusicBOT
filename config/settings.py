from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений переменных из файла .env с указанием типа данных и значений по умолчанию
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Токен бота Discord
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')  # API ключ для YouTube
BOT_PREFIX = os.getenv('BOT_PREFIX')  # Префикс команд бота
OWNER_ID = os.getenv('OWNER_ID')  # ID владельца бота
EMBEDCOLOR = int(os.getenv('EMBEDCOLOR', '0xF8AA2A'), 16)  # Цвет для встраиваемых сообщений, значение по умолчанию 0xF8AA2A
BOT_ACTIVITY_TYPE = int(os.getenv('BOT_ACTIVITY_TYPE', 0))  # Тип активности бота, значение по умолчанию 0
BOT_ACTIVITY_NAME = os.getenv('BOT_ACTIVITY_NAME', '')  # Название активности бота, значение по умолчанию пустая строка
PLAYLIST_SONG_COUNT = int(os.getenv('PLAYLIST_SONG_COUNT', 0))  # Количество песен в плейлисте, значение по умолчанию 0
WELCOME_ROLE_ID = os.getenv('WELCOME_ROLE_ID')  # ID роли для приветствия новых участников
