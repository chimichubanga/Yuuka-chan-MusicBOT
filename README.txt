# Yuuka-chan Music Bot

Yuuka-chan - это музыкальный бот для Discord, который может проигрывать музыку из YouTube.

1. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

2. Создайте файл `.env` и добавьте ваши конфигурационные параметры:
    ```env
    BOT_TOKEN=your_bot_token
    YOUTUBE_API_KEY=your_youtube_api_key
    BOT_PREFIX=+
    OWNER_ID=your_owner_id
    EMBEDCOLOR=0xF8AA2A
    BOT_ACTIVITY_TYPE=0
    BOT_ACTIVITY_NAME=
    PLAYLIST_SONG_COUNT=0
    WELCOME_ROLE_ID=your_welcome_role_id
    ```

## Запуск

```bash
python main.py
