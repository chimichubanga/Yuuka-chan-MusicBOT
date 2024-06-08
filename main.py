import discord
from discord.ext import commands
import asyncio
import platform
from colorama import Back, Fore, Style
import time
from config import BOT_TOKEN, BOT_PREFIX

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(BOT_PREFIX), intents=discord.Intents().all())

        self.cogslist = ["cogs.music", "cogs.cmd", "cogs.admin"]

    async def setup_hook(self):
        for ext in self.cogslist:
            await self.load_extension(ext)

    async def on_ready(self):
        # Получаем текущее время в формате UTC
        prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
    
        # Логируем информацию о боте
        print(prfx + Fore.LIGHTBLUE_EX + " 🔸🔹🔸 Yuuka-chan готова к работе, сенсей! 🔸🔹🔸")
        print(prfx + " ✨ Логин под именем: " + Fore.YELLOW + self.user.name)
        print(prfx + " 🆔 ID бота: " + Fore.YELLOW + str(self.user.id))
        print(prfx + " 📅 Версия Discord: " + Fore.YELLOW + discord.__version__)
        print(prfx + " 🐍 Версия Python: " + Fore.YELLOW + str(platform.python_version()))
    
        # Синхронизация команд
        synced = await self.tree.sync()
        print(prfx + " 🎵 Slash CMDs синхронизированы: " + Fore.YELLOW + str(len(synced)) + " команд")
        print(prfx + Fore.LIGHTBLUE_EX + " 🔸🔹🔸 Yuuka-chan в вашем распоряжении, сенсей! 🔸🔹🔸")

client = Client()

client.run(BOT_TOKEN)
