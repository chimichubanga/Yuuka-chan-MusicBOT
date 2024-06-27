import discord
from discord.ext import commands
import asyncio
import platform
from colorama import Back, Fore, Style
import time
from config import BOT_TOKEN, BOT_PREFIX
import logging
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка логирования для библиотеки discord.py
logging.getLogger('discord.client').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.player').setLevel(logging.WARNING)
logging.getLogger('discord.voice_client').setLevel(logging.WARNING)

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(BOT_PREFIX), intents=discord.Intents().all())
        self.cogslist = ["cogs.music", "cogs.cmd", "cogs.admin"]
        # Установим количество шагов прогресс-бара в зависимости от количества когов и дополнительных этапов
        self.total_steps = 100
        self.steps_per_stage = self.total_steps // (len(self.cogslist) + 5)
        self.loading_bar = tqdm(total=self.total_steps, desc="Запуск бота", bar_format="{l_bar}{bar} [Время: {elapsed}]", ncols=100)

    async def setup_hook(self):
        # Шаг 1: Проверка конфигурации
        self.loading_bar.set_description("Проверка конфигурации")
        for _ in range(self.steps_per_stage):
            await asyncio.sleep(0.05)  # Пауза для плавного увеличения
            self.loading_bar.update(1)

        # Шаг 2: Загрузка библиотек
        self.loading_bar.set_description("Загрузка библиотек")
        for _ in range(self.steps_per_stage):
            await asyncio.sleep(0.05)  # Пауза для плавного увеличения
            self.loading_bar.update(1)

        # Шаг 3: Загрузка когов
        for ext in self.cogslist:
            self.loading_bar.set_description(f"Загрузка {ext}")
            await self.load_extension(ext)
            for _ in range(self.steps_per_stage):
                await asyncio.sleep(0.05)  # Пауза для плавного увеличения
                self.loading_bar.update(1)

        # Шаг 4: Установка соединений
        self.loading_bar.set_description("Установка соединений")
        for _ in range(self.steps_per_stage):
            await asyncio.sleep(0.05)  # Пауза для плавного увеличения
            self.loading_bar.update(1)

    async def on_ready(self):
        # Шаг 5: Синхронизация команд
        self.loading_bar.set_description("Синхронизация команд")
        synced = await self.tree.sync()
        for _ in range(self.steps_per_stage):
            await asyncio.sleep(0.05)  # Пауза для плавного увеличения
            self.loading_bar.update(1)

        # Шаг 6: Финализация запуска
        self.loading_bar.set_description("Финализация запуска")
        for _ in range(self.steps_per_stage):
            await asyncio.sleep(0.05)  # Пауза для плавного увеличения
            self.loading_bar.update(1)

        # Обновим оставшиеся шаги, если прогресс-бар еще не заполнен
        remaining_steps = self.total_steps - self.loading_bar.n
        self.loading_bar.set_description("Бот готов к работе")
        for _ in range(remaining_steps):
            await asyncio.sleep(0.05)
            self.loading_bar.update(1)
        self.loading_bar.close()

        prfx = (Back.BLACK + Fore.CYAN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)

        # Тематическое сообщение
        print(Style.BRIGHT + Fore.CYAN + "╔═════════════════════════════════════════════════════════╗")
        print(Fore.CYAN + "║" + Style.BRIGHT + Fore.LIGHTBLUE_EX + "          Yuuka-chan готова к работе, сенсей!            " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚═════════════════════════════════════════════════════════╝" + Style.RESET_ALL)
        print(prfx + Fore.LIGHTBLUE_EX + " ✨ Логин под именем: " + Fore.YELLOW + self.user.name)
        print(prfx + Fore.LIGHTBLUE_EX + " 🆔 ID бота: " + Fore.YELLOW + str(self.user.id))
        print(prfx + Fore.LIGHTBLUE_EX + " 📅 Версия Discord: " + Fore.YELLOW + discord.__version__)
        print(prfx + Fore.LIGHTBLUE_EX + " 🐍 Версия Python: " + Fore.YELLOW + str(platform.python_version()))
        print(prfx + Fore.LIGHTBLUE_EX + " 🎵 Slash CMDs синхронизированы: " + Fore.YELLOW + str(len(synced)) + " команд")
        print(Fore.CYAN + "╔═════════════════════════════════════════════════════════╗")
        print(Fore.CYAN + "║" + Style.BRIGHT + Fore.LIGHTBLUE_EX + "          Yuuka-chan в вашем распоряжении, сенсей!       " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚═════════════════════════════════════════════════════════╝" + Style.RESET_ALL)

if __name__ == "__main__":
    with logging_redirect_tqdm():
        client = Client()
        client.run(BOT_TOKEN)
