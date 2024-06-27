# cogs/cmd.py

import discord
from discord.ext import commands
from config import WELCOME_ROLE_ID
import logging

logger = logging.getLogger(__name__)

class Cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = member.guild.get_role(int(WELCOME_ROLE_ID))
        if role is not None:
            await member.add_roles(role)
            logger.info(f"{member} получил(a) роль при входе на сервер.")
        else:
            logger.warning(f"Роль с ID {WELCOME_ROLE_ID} не найдена на сервере.")

async def setup(bot):
    await bot.add_cog(Cmd(bot))