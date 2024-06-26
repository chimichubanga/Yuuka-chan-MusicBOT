# cogs/music.py

import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp as youtube_dl
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import YOUTUBE_API_KEY, EMBEDCOLOR
import logging
from youtube_search import YoutubeSearch
from pytube import YouTube
from PIL import Image
from io import BytesIO
import re
import requests

logger = logging.getLogger(__name__)

queue = []
repeat_queue = False

def clean_filename(filename):
    cleaned_filename = re.sub(r'[\\/:"*?<>|]', '_', filename)
    return cleaned_filename

class GuildMusicPlayer:
    def __init__(self, bot, voice_client, yt, stream_url):
        self.bot = bot
        self.voice_client = voice_client
        self.yt = yt
        self.stream_url = stream_url
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -af aresample=async=1'
        }
        self.loop = False
        self.message = None  # Храним сообщение с кнопками
        self.update_view_task = None  # Задача для обновления кнопок

    def play(self):
        self.voice_client.play(discord.FFmpegPCMAudio(self.stream_url, **self.ffmpeg_options), after=self.after_playback)

    def after_playback(self, error):
        if error:
            logger.error(f'Error during playback: {error}')
        asyncio.run_coroutine_threadsafe(self._after_playback(), self.bot.loop)

    async def _after_playback(self):
        if self.loop:
            self.play()
        else:
            if self.voice_client:
                await self.voice_client.disconnect()
            if self.message:
                await self.message.delete()  # Удаляем сообщение после завершения воспроизведения
            if self.update_view_task:
                self.update_view_task.cancel()  # Останавливаем обновление кнопок

    async def update_view(self):
        while True:
            if self.message:
                await self.message.edit(view=MusicView(self))  # Обновляем сообщение с кнопками
            await asyncio.sleep(150)  # Ждем 10 минут

class MusicView(discord.ui.View):
    def __init__(self, player):
        super().__init__()
        self.player = player

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.blurple)
    async def repeat(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.loop = not self.player.loop
        await interaction.response.defer()
        await interaction.followup.send(f"Режим повтора {'включен' if self.player.loop else 'выключен'}.", ephemeral=True)

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.blurple)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player.voice_client.is_playing():
            self.player.voice_client.pause()
        await interaction.response.defer()

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.player.voice_client.is_paused():
            self.player.voice_client.resume()
        await interaction.response.defer()

    @discord.ui.button(emoji="⛔", style=discord.ButtonStyle.grey)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_state = interaction.guild.get_member(interaction.user.id).voice
        if voice_state is None or voice_state.channel is None:
            await interaction.response.send_message("Вы должны быть в голосовом канале, чтобы использовать эту команду.")
            return
        await interaction.response.defer()

        try:
            voice_client = discord.utils.get(self.player.bot.voice_clients, guild=interaction.guild)
            if voice_client and voice_client.is_playing():
                voice_client.stop()
                await interaction.followup.send("Воспроизведение музыки остановлено.", ephemeral=True)
                await voice_client.disconnect()
            else:
                await interaction.followup.send("В данный момент ничего не воспроизводится.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f'Произошла ошибка: {e}', ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="присоединиться", description="Присоединить Yuuka-chan к голосовому каналу")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("Сенсей, пожалуйста, зайдите в голосовой канал, чтобы Yuuka-chan могла присоединиться.", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client is not None:
            await voice_client.move_to(channel)
        else:
            await channel.connect()
        await interaction.response.send_message("Yuuka-chan к вашим услугам, сенсей", ephemeral=True)

    @app_commands.command(name="отключится", description="Отключить Yuuka-chan от голосового канала")
    async def disconnect(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client is not None or voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("Yuuka-chan больше не подключена к каналу, сенсей", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не подключена к голосовому каналу, сенсей", ephemeral=True)

    @app_commands.command(name="играть", description="Воспроизвести музыку по запросу")
    async def play(self, interaction: discord.Interaction, запрос: str):
        voice_state = interaction.guild.get_member(interaction.user.id).voice
        if voice_state is None or voice_state.channel is None:
            await interaction.response.send_message("Вы должны быть в голосовом канале, чтобы использовать эту команду.")
            return

        await interaction.response.defer()

        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()

        try:
            voice_client = await voice_state.channel.connect()

            if запрос.startswith("http"):
                video_url = запрос
            else:
                results = YoutubeSearch(запрос, max_results=1).to_dict()
                if not results:
                    await interaction.followup.send("По вашему запросу ничего не найдено.")
                    return
                video_url = "https://www.youtube.com" + results[0]['url_suffix']

            # Используем yt-dlp для получения прямого URL потока
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'extract_flat': 'in_playlist'
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                stream_url = info['url']

            yt = YouTube(video_url)

            # Создание встроенного сообщения (embed)
            spacer = '--' * 34
            embed = discord.Embed(title=yt.title, description=f"Длительность: {yt.length // 60}:{yt.length % 60:02d}\n{spacer}", color=0x1E90FF)
            embed.set_footer(text=f"added by {interaction.user.display_name}")
            embed.set_thumbnail(url=yt.thumbnail_url)  # Устанавливаем URL превью-изображения

            player = GuildMusicPlayer(self.bot, voice_client, yt, stream_url)
            player.play()

            # Отправляем сообщение с кнопками и сохраняем его в player
            player.message = await interaction.followup.send(embed=embed, view=MusicView(player))

            # Запускаем задачу для обновления кнопок
            player.update_view_task = asyncio.create_task(player.update_view())
            
        except Exception as e:
            await interaction.followup.send(f'Произошла ошибка: {e}', ephemeral=True)

    @app_commands.command(name="stop", description="Остановить воспроизведение музыки")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("Воспроизведение остановлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="pause", description="Приостановить воспроизведение музыки")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Воспроизведение приостановлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="resume", description="Возобновить воспроизведение музыки")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Воспроизведение возобновлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="repeat", description="Включить/выключить повтор текущей песни")
    async def repeat(self, interaction: discord.Interaction):
        global repeat_queue
        repeat_queue = not repeat_queue
        if repeat_queue:
            await interaction.response.send_message("Повтор включен, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Повтор выключен, сенсей.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
