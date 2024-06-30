import discord
from discord.ext import commands
import asyncio
import platform
from colorama import Back, Fore, Style
import time
import os
from config.settings import BOT_TOKEN, BOT_PREFIX
import logging
from utils.progress_bar import ProgressBar
from utils.logger import setup_logging

setup_logging()

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(BOT_PREFIX), intents=discord.Intents().all())
        self.cogslist = ["cogs.music", "cogs.cmd", "cogs.admin", "cogs.games"]
        self.progress_bar = ProgressBar(len(self.cogslist) + 5)

    async def setup_hook(self):
        stages = ["Проверка конфигурации", "Загрузка библиотек", "Загрузка когов", "Установка соединений", "Синхронизация команд", "Финализация запуска"]
        for stage in stages:
            self.progress_bar.update_stage(stage)
            await asyncio.sleep(0.05)
            if stage == "Загрузка когов":
                for ext in self.cogslist:
                    await self.load_extension(ext)
                    self.progress_bar.update_stage(f"Загрузка {ext}")

    async def on_ready(self):
        self.progress_bar.finish()
        
        # Очистка консоли
        await self.clear_console()

        prfx = (Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)

        print(Style.BRIGHT + Fore.CYAN + "╔═════════════════════════════════════════════════════════╗")
        print(Fore.CYAN + "║" + Style.BRIGHT + Fore.LIGHTBLUE_EX + "          Yuuka-chan готова к работе, сенсей!            " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚═════════════════════════════════════════════════════════╝" + Style.RESET_ALL)
        print(prfx + Fore.LIGHTBLUE_EX + " ✨ Логин под именем: " + Fore.YELLOW + self.user.name)
        print(prfx + Fore.LIGHTBLUE_EX + " 🆔 ID бота: " + Fore.YELLOW + str(self.user.id))
        print(prfx + Fore.LIGHTBLUE_EX + " 📅 Версия Discord: " + Fore.YELLOW + discord.__version__)
        print(prfx + Fore.LIGHTBLUE_EX + " 🐍 Версия Python: " + Fore.YELLOW + str(platform.python_version()))
        print(prfx + Fore.LIGHTBLUE_EX + " 🎵 Slash CMDs синхронизированы: " + Fore.YELLOW + str(len(await self.tree.sync())) + " команд")
        print(Fore.CYAN + "╔═════════════════════════════════════════════════════════╗")
        print(Fore.CYAN + "║" + Style.BRIGHT + Fore.LIGHTBLUE_EX + "          Yuuka-chan в вашем распоряжении, сенсей!       " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚═════════════════════════════════════════════════════════╝" + Style.RESET_ALL)

    async def clear_console(self):
        # Определение команды для очистки консоли в зависимости от операционной системы
        command = "cls" if platform.system() == "Windows" else "clear"
        os.system(command)

if __name__ == "__main__":
    client = Client()
    client.run(BOT_TOKEN)
