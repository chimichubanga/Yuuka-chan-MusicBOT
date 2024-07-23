import logging

def setup_logging():
    # Настройка основного логирования с уровнем INFO
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Установка уровней логирования для модулей discord.py
    #logging.getLogger('discord.client').setLevel(logging.WARNING)
    #logging.getLogger('discord.gateway').setLevel(logging.WARNING)
    #logging.getLogger('discord.player').setLevel(logging.WARNING)
    #logging.getLogger('discord.voice_client').setLevel(logging.WARNING)
    
    # Логирование для состояния голосовых каналов
    #logging.getLogger('discord.voice_state').setLevel(logging.ERROR)

# Вызов функции для настройки логирования
setup_logging()
