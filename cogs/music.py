import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp as youtube_dl
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import YOUTUBE_API_KEY, PLAYLIST_SONG_COUNT, EMBEDCOLOR

queue = []
repeat_queue = False

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
        if voice_client is not None and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("Yuuka-chan больше не подключена к каналу, сенсей", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не подключена к голосовому каналу, сенсей", ephemeral=True)

    @app_commands.command(name="играть", description="Воспроизвести музыку по запросу")
    async def play(self, interaction: discord.Interaction, query: str):
        try:
            channel = interaction.user.voice.channel
        except AttributeError:
            await interaction.response.send_message("Сенсей, пожалуйста, зайдите в голосовой канал, чтобы использовать эту команду.", ephemeral=True)
            return

        if not channel.permissions_for(interaction.guild.me).connect:
            await interaction.response.send_message("Yuuka-chan не может подключиться к голосовому каналу, сенсей.", ephemeral=True)
            return

        voice_channel = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_channel:
            if voice_channel.channel != channel:
                await interaction.response.send_message("Yuuka-chan уже находится в другом голосовом канале, сенсей.", ephemeral=True)
                return
        else:
            voice_channel = await channel.connect()

        if 'youtu.be' in query or 'youtube.com' in query:
            video_id = self.extract_video_id(query)
            if not video_id:
                await interaction.response.send_message("Yuuka-chan не смогла извлечь ID видео, сенсей.", ephemeral=True)
                return
            url = f'https://www.youtube.com/watch?v={video_id}'
            await self.process_single_song(interaction, voice_channel, video_id, url)
        else:
            video_id = self.search_youtube(query)
            if not video_id:
                await interaction.response.send_message("Yuuka-chan не нашла результатов по данному запросу, сенсей.", ephemeral=True)
                return
            url = f'https://www.youtube.com/watch?v={video_id}'
            await self.process_single_song(interaction, voice_channel, video_id, url)

    async def process_single_song(self, interaction, voice_channel, video_id, url):
        title = self.get_video_title(video_id)
        await interaction.response.send_message(f"Добавлено в очередь, сенсей: **{title}**")

        queue.append({
            'url': url,
            'title': title
        })

        if not voice_channel.is_playing():
            await self.play_next_in_queue(voice_channel)

    def extract_video_id(self, url):
        if 'youtube.com' in url:
            query = url.split('watch?v=')[-1]
            return query.split('&')[0]
        elif 'youtu.be' in url:
            return url.split('/')[-1]
        return None

    def get_video_title(self, video_id):
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        try:
            request = youtube.videos().list(part='snippet', id=video_id)
            response = request.execute()
            return response['items'][0]['snippet']['title']
        except HttpError as e:
            print(f'Произошла ошибка, сенсей: {e}')
            return None

    def search_youtube(self, query):
        ydl = youtube_dl.YoutubeDL({'format': 'bestaudio'})
        try:
            with ydl:
                result = ydl.extract_info(f'ytsearch:{query}', download=False)
                return result['entries'][0]['id']
        except youtube_dl.DownloadError:
            return None

    async def play_next_in_queue(self, voice_channel):
        if not queue:
            return

        next_song = queue.pop(0)
        url = next_song['url']

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'audioformat': 'mp3',
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            audio_url = info_dict['url']

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        def after_playing(error):
            if repeat_queue:
                queue.append(next_song)
            asyncio.run_coroutine_threadsafe(self.play_next_in_queue(voice_channel), self.bot.loop)

        voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_url, **ffmpeg_options), after=after_playing)
        voice_channel.source = discord.PCMVolumeTransformer(voice_channel.source, volume=0.5)

    @app_commands.command(name="очередь", description="Показать очередь воспроизведения")
    async def display_queue(self, interaction: discord.Interaction):
        if not queue:
            await interaction.response.send_message("Очередь пуста, сенсей.", ephemeral=True)
            return

        embed = discord.Embed(title="Очередь воспроизведения", color=int(EMBEDCOLOR, 16))
        for idx, song in enumerate(queue, start=1):
            embed.add_field(name=f"{idx}.", value=song['title'], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="возобновить", description="Возобновить воспроизведение")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Воспроизведение возобновлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="пауза", description="Приостановить воспроизведение")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Воспроизведение приостановлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="пропустить", description="Пропустить текущую песню")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("Пропущено, сенсей.", ephemeral=True)
            await self.play_next_in_queue(voice_client)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="стоп", description="Остановить воспроизведение")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("Воспроизведение остановлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="повтор", description="Включить/выключить повтор очереди")
    async def repeat(self, interaction: discord.Interaction):
        global repeat_queue
        repeat_queue = not repeat_queue
        if repeat_queue:
            await interaction.response.send_message("Повтор очереди включен, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Повтор очереди выключен, сенсей.", ephemeral=True)

    @app_commands.command(name="очистить", description="Очистить очередь воспроизведения")
    async def clear_queue(self, interaction: discord.Interaction):
        global queue
        queue = []
        await interaction.response.send_message("Очередь очищена, сенсей.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
