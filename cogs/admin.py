import discord
from discord.ext import commands
from discord import app_commands
from config.settings import OWNER_ID
import logging

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="выключение", description="Остановить работу Yuuka-chan (только для владельца)")
    @app_commands.checks.has_permissions(administrator=True)
    async def shutdown(self, interaction: discord.Interaction):
        # Команда для отключения бота (только для владельца)
        if interaction.user.id == int(OWNER_ID):
            await interaction.response.send_message("Yuuka-chan отключается, сенсей...", ephemeral=True)
            logger.info("Yuuka-chan отключается, сенсей...")
            await self.bot.close()
        else:
            await interaction.response.send_message("У вас нет прав для этой команды, сенсей.", ephemeral=True)

    @app_commands.command(name="очистить_канал", description="Очистить канал (необходимы права на управление сообщениями)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_channel(self, interaction: discord.Interaction, limit: int):
        # Команда для очистки канала
        await interaction.response.send_message(f"Очищено {limit} сообщений, сенсей.", ephemeral=True)
        await interaction.channel.purge(limit=limit)

    @app_commands.command(name="пинг", description="Проверить задержку бота")
    async def ping(self, interaction: discord.Interaction):
        # Команда для проверки задержки бота
        latency = self.bot.latency * 1000  # Преобразуем задержку в миллисекунды
        await interaction.response.send_message(f"Понг! Задержка: {latency:.2f}мс", ephemeral=True)

    @app_commands.command(name="юзеринфо", description="Получить информацию о пользователе")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member):
        # Команда для получения информации о пользователе
        embed = discord.Embed(title=f"Информация о пользователе {member.name}", color=0x1E90FF)
        embed.add_field(name="ID пользователя", value=member.id, inline=True)
        embed.add_field(name="Имя", value=member.display_name, inline=True)
        embed.add_field(name="Создан", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
        embed.add_field(name="Присоединился", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
        embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="серверинфо", description="Получить информацию о сервере")
    async def serverinfo(self, interaction: discord.Interaction):
        # Команда для получения информации о сервере
        guild = interaction.guild
        embed = discord.Embed(title=f"Информация о сервере {guild.name}", color=0x1E90FF)
        embed.add_field(name="ID сервера", value=guild.id, inline=True)
        embed.add_field(name="Создан", value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
        embed.add_field(name="Владелец", value=guild.owner.mention, inline=True)
        embed.add_field(name="Участники", value=guild.member_count, inline=True)
        embed.set_thumbnail(url=guild.icon.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
