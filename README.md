
```markdown
# 🌸 Yuuka-chan Music Bot 🌸

Добро пожаловать, сенсей! Yuuka-chan здесь, чтобы украсить ваш сервер Discord музыкой и весельем. 🎵

## 🌟 Особенности

- **🎶 Воспроизведение музыки**: Наслаждайтесь любимыми треками из YouTube.
- **📜 Очередь и История**: Контролируйте очередь воспроизведения и просматривайте историю треков.
- **🕹️ Управление плеером**: Используйте интерактивные кнопки для управления воспроизведением.
- **🔄 Динамические кнопки**: Кнопки автоматически обновляются в зависимости от текущего состояния.
- **✨ Интерактивные команды**: Присоединяйтесь, отключайтесь и управляйте плеером с помощью простых команд.

## 🛠️ Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/chimichubanga/Yuuka-chan-MusicBOT.git
    ```
2. Перейдите в директорию проекта:
    ```bash
    cd Yuuka-chan-MusicBOT
    ```
3. Установите необходимые зависимости:
    ```bash
    pip install -r requirements.txt
    ```
4. Создайте файл `.env` в корне проекта и добавьте ваши настройки:
    ```env
    BOT_TOKEN=your_discord_bot_token
    YOUTUBE_API_KEY=your_youtube_api_key
    BOT_PREFIX=!
    OWNER_ID=your_discord_user_id
    EMBEDCOLOR=0xF8AA2A
    BOT_ACTIVITY_TYPE=0
    BOT_ACTIVITY_NAME=Listening to music
    PLAYLIST_SONG_COUNT=10
    WELCOME_ROLE_ID=your_welcome_role_id
    ```

## 🚀 Использование

Запустите Yuuka-chan:
```bash
python main.py
```

### 🏆 Основные команды

- `/присоединиться`: Присоединить Yuuka-chan к голосовому каналу.
- `/отключится`: Отключить Yuuka-chan от голосового канала.
- `/играть <запрос>`: Воспроизвести музыку по запросу.
- `/плеер`: Показать текущий плеер.
- `/stop`: Остановить воспроизведение музыки.
- `/pause`: Приостановить воспроизведение музыки.
- `/resume`: Возобновить воспроизведение музыки.
- `/repeat`: Включить/выключить повтор текущей песни.

## 🤝 Вклад

Если вы хотите помочь Yuuka-chan стать ещё лучше, следуйте этим шагам:

1. Форкните репозиторий.
2. Создайте новую ветку:
    ```bash
    git checkout -b feature/your-feature-name
    ```
3. Внесите свои изменения и сделайте коммит:
    ```bash
    git commit -m "Добавлена новая функция: your-feature-name"
    ```
4. Отправьте свои изменения на GitHub:
    ```bash
    git push origin feature/your-feature-name
    ```
5. Создайте Pull Request.

## 📜 Лицензия

Этот проект лицензируется в соответствии с [MIT License](LICENSE).

---

Yuuka-chan всегда готова помочь вам насладиться прекрасной музыкой! 🌸🎵

