import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    #discord.py
    logging.getLogger('discord.client').setLevel(logging.WARNING)
    logging.getLogger('discord.gateway').setLevel(logging.WARNING)
    logging.getLogger('discord.player').setLevel(logging.WARNING)
    logging.getLogger('discord.voice_client').setLevel(logging.WARNING)
    
    #discord.voice_state
    logging.getLogger('discord.voice_state').setLevel(logging.ERROR)
