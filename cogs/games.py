import discord
from discord.ext import commands
from discord import app_commands
import random

# Ког (расширение) для игровых команд
class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ролл", description="Бросить кости")
    async def roll(self, interaction: discord.Interaction, number: int):
        # Команда для броска кубика
        result = random.randint(1, number)  # Генерация случайного числа от 1 до number
        await interaction.response.send_message(f"🎲 Вы бросили {number}-сторонний кубик и выпало: {result}")

    @app_commands.command(name="флип", description="Подбросить монету")
    async def flip(self, interaction: discord.Interaction):
        # Команда для подбрасывания монеты
        result = random.choice(["Орёл", "Решка"])  # Случайный выбор между Орлом и Решкой
        await interaction.response.send_message(f"🪙 Результат подбрасывания монеты: {result}")

    @app_commands.command(name="8шар", description="Вопросы к магическому шару")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        # Команда для вопросов к магическому шару
        responses = [
            "Да.", "Нет.", "Возможно.", "Спросите позже.", 
            "Точно да.", "Точно нет."
        ]
        response = random.choice(responses)  # Случайный выбор ответа из списка
        await interaction.response.send_message(f"🎱 Магический шар говорит: {response}")

    @app_commands.command(name="крестики-нолики", description="Игра в крестики-нолики")
    async def tictactoe(self, interaction: discord.Interaction, user: discord.Member):
        # Команда для игры в крестики-нолики (еще не реализована)
        await interaction.response.send_message("Игра в крестики-нолики еще не реализована.", ephemeral=True)

# Функция для добавления кода в бот
async def setup(bot):
    await bot.add_cog(Games(bot))
