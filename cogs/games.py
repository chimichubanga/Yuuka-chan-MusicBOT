import discord
from discord.ext import commands
from discord import app_commands
import random

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ролл", description="Бросить кости")
    async def roll(self, interaction: discord.Interaction, number: int):
        result = random.randint(1, number)
        await interaction.response.send_message(f"🎲 Вы бросили {number}-сторонний кубик и выпало: {result}")

    @app_commands.command(name="флип", description="Подбросить монету")
    async def flip(self, interaction: discord.Interaction):
        result = random.choice(["Орёл", "Решка"])
        await interaction.response.send_message(f"🪙 Результат подбрасывания монеты: {result}")

    @app_commands.command(name="8шар", description="Вопросы к магическому шару")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "Да.", "Нет.", "Возможно.", "Спросите позже.", "Точно да.", "Точно нет."
        ]
        response = random.choice(responses)
        await interaction.response.send_message(f"🎱 Магический шар говорит: {response}")

    @app_commands.command(name="крестики-нолики", description="Игра в крестики-нолики")
    async def tictactoe(self, interaction: discord.Interaction, user: discord.Member):
        # Логика игры в крестики-нолики будет здесь
        await interaction.response.send_message("Игра в крестики-нолики еще не реализована.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Games(bot))
