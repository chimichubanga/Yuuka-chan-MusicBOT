import discord
from discord.ext import commands
from config.settings import WELCOME_ROLE_ID
import logging

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

# Ког (расширение) для команд
class Cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Обработка события присоединения нового участника
        role = member.guild.get_role(int(WELCOME_ROLE_ID))  # Получение роли по ID
        if role is not None:
            await member.add_roles(role)  # Добавление роли новому участнику
            logger.info(f"{member} получил(a) роль при входе на сервер.")  # Логирование добавления роли
        else:
            logger.warning(f"Роль с ID {WELCOME_ROLE_ID} не найдена на сервере.")  # Логирование предупреждения, если роль не найдена

# Функция для добавления кода в бот
async def setup(bot):
    await bot.add_cog(Cmd(bot))
