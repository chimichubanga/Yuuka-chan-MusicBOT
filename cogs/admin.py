# cogs/admin.py

import discord
from discord.ext import commands
from discord import app_commands
from config import OWNER_ID
import logging

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="выключение", description="Остановить работу Yuuka-chan (только для владельца)")
    @app_commands.checks.has_permissions(administrator=True)
    async def shutdown(self, interaction: discord.Interaction):
        if interaction.user.id == int(OWNER_ID):
            await interaction.response.send_message("Yuuka-chan отключается, сенсей...", ephemeral=True)
            logger.info("Yuuka-chan отключается, сенсей...")
            await self.bot.close()
        else:
            await interaction.response.send_message("У вас нет прав для этой команды, сенсей.", ephemeral=True)

    @app_commands.command(name="очистить_канал", description="Очистить канал (необходимы права на управление сообщениями)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_channel(self, interaction: discord.Interaction, limit: int):
        await interaction.response.send_message(f"Очищено {limit} сообщений, сенсей.", ephemeral=True)
        await interaction.channel.purge(limit=limit)

    @app_commands.command(name="ping", description="Проверить задержку бота")
    async def ping(self, interaction: discord.Interaction):
        latency = self.bot.latency * 1000  # Преобразуем задержку в миллисекунды
        await interaction.response.send_message(f"Понг! Задержка: {latency:.2f}мс", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
