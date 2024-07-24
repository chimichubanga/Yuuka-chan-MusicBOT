# Импорт необходимых библиотек и модулей
import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp as youtube_dl
import asyncio
import logging
from youtube_search import YoutubeSearch
from pytube import YouTube
from youtubesearchpython import VideosSearch
from config.settings import YOUTUBE_API_KEY

# Настройка логирования для данного модуля
logger = logging.getLogger(__name__)

# Класс для управления музыкой на сервере
class GuildMusicPlayer:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.voice_client = None  # Клиент голосового канала
        self.queue = []  # Очередь воспроизведения
        self.history = []  # История воспроизведения
        self.current = None  # Текущий трек
        self.loop = False  # Режим повтора
        self.message = None  # Сообщение о текущем треке
        self.afk_timer = None  # Таймер бездействия
        # Опции для FFMPEG, используемого для воспроизведения аудио
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -af aresample=async=1'
        }

    async def connect(self, channel):
        # Подключение к голосовому каналу
        if self.voice_client is None or not self.voice_client.is_connected():
            self.voice_client = await channel.connect(reconnect=True)

    def add_to_queue(self, yt, stream_url, interaction):
        # Добавление трека в очередь
        self.queue.append((yt, stream_url, interaction))
        self.cancel_afk_timer()

    async def play_next(self):
        # Воспроизведение следующего трека из очереди
        if self.queue:
            if self.current:
                # Добавление текущего трека в историю
                self.history.append(self.current)
                if len(self.history) > 6:
                    self.history.pop(0)
            self.current = self.queue.pop(0)
            yt, stream_url, interaction = self.current
            # Воспроизведение следующего трека
            self.voice_client.play(discord.FFmpegPCMAudio(stream_url, **self.ffmpeg_options), after=lambda e: self.bot.loop.create_task(self.after_playback(e)))
            await self.send_now_playing_message(yt)
        else:
            self.current = None
            self.start_afk_timer()

    async def play_previous(self):
        # Воспроизведение предыдущего трека из истории
        if self.history:
            if self.current:
                # Возвращение текущего трека в очередь
                self.queue.insert(0, self.current)
            self.current = self.history.pop()
            yt, stream_url, interaction = self.current
            # Воспроизведение предыдущего трека
            self.voice_client.play(discord.FFmpegPCMAudio(stream_url, **self.ffmpeg_options), after=lambda e: self.bot.loop.create_task(self.after_playback(e)))
            await self.send_now_playing_message(yt)
        else:
            await self.send_no_previous_message()

    async def send_now_playing_message(self, yt):
        # Отправка сообщения о текущем воспроизводимом треке
        embed = discord.Embed(
            title=yt.title,
            description=f"Длительность: {yt.length // 60}:{yt.length % 60:02d}",
            color=0x1E90FF
        )
        embed.set_footer(text=f"added by {self.current[2].user.display_name}")
        embed.set_thumbnail(url=yt.thumbnail_url)

        if self.message:
            await self.message.edit(embed=embed, view=MusicView(self))
        else:
            channel = self.current[2].channel
            self.message = await channel.send(embed=embed, view=MusicView(self))

    async def send_no_previous_message(self):
        # Отправка сообщения об отсутствии предыдущих треков в истории
        if self.message:
            await self.message.channel.send("Нет предыдущего трека в истории.", delete_after=10)

    def play(self):
        # Начало воспроизведения следующего трека
        asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop)

    async def after_playback(self, error):
        # Действия после окончания воспроизведения трека
        if error:
            logger.error(f'Error during playback: {error}')
        if self.loop and self.current:
            yt, stream_url, interaction = self.current
            self.queue.insert(0, (yt, stream_url, interaction))
        await self.play_next()

    def start_afk_timer(self):
        # Запуск таймера бездействия
        if self.afk_timer:
            self.afk_timer.cancel()
        self.afk_timer = self.bot.loop.call_later(300, lambda: asyncio.run_coroutine_threadsafe(self.disconnect_afk(), self.bot.loop))

    def cancel_afk_timer(self):
        # Отмена таймера бездействия
        if self.afk_timer:
            self.afk_timer.cancel()
            self.afk_timer = None

    async def disconnect_afk(self):
        # Отключение при бездействии
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
            logger.info(f"Bot disconnected from {self.guild.name} due to inactivity.")

# Класс для интерфейса управления музыкой через кнопки
class MusicView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player
        self.add_buttons()
        self.update_play_pause_button()

    def add_buttons(self):
        # Добавление кнопок управления плеером
        self.previous_button = discord.ui.Button(emoji="⏮️", style=discord.ButtonStyle.blurple)
        self.previous_button.callback = self.previous
        self.add_item(self.previous_button)

        self.play_pause_button = discord.ui.Button(emoji="▶️", style=discord.ButtonStyle.blurple, custom_id="play_pause")
        self.play_pause_button.callback = self.play_pause
        self.add_item(self.play_pause_button)

        self.next_button = discord.ui.Button(emoji="⏭️", style=discord.ButtonStyle.blurple)
        self.next_button.callback = self.next
        self.add_item(self.next_button)

        self.repeat_button = discord.ui.Button(emoji="🔁", style=discord.ButtonStyle.blurple)
        self.repeat_button.callback = self.repeat
        self.add_item(self.repeat_button)

        self.stop_button = discord.ui.Button(emoji="⛔", style=discord.ButtonStyle.grey)
        self.stop_button.callback = self.stop
        self.add_item(self.stop_button)

    def update_play_pause_button(self):
        # Обновление состояния кнопки воспроизведения/паузы
        if self.player.voice_client and self.player.voice_client.is_playing():
            self.play_pause_button.emoji = "⏸️"
        else:
            self.play_pause_button.emoji = "▶️"
        self.play_pause_button.style = discord.ButtonStyle.blurple
        self.play_pause_button.disabled = False

    async def previous(self, interaction: discord.Interaction):
        # Обработка нажатия кнопки предыдущего трека
        if self.player.voice_client.is_playing() or self.player.voice_client.is_paused():
            self.player.voice_client.stop()
        await self.player.play_previous()
        self.update_play_pause_button()
        await interaction.response.defer()

    async def repeat(self, interaction: discord.Interaction):
        # Обработка нажатия кнопки повтора
        self.player.loop = not self.player.loop
        await interaction.response.defer()
        await interaction.followup.send(f"Режим повтора {'включен' if self.player.loop else 'выключен'}.", ephemeral=True)

    async def play_pause(self, interaction: discord.Interaction):
        # Обработка нажатия кнопки воспроизведения/паузы
        if self.player.voice_client.is_playing():
            self.player.voice_client.pause()
            self.play_pause_button.emoji = "▶️"
        else:
            self.player.voice_client.resume()
            self.play_pause_button.emoji = "⏸️"
        await interaction.response.defer()
        self.update_play_pause_button()

    async def next(self, interaction: discord.Interaction):
        # Обработка нажатия кнопки следующего трека
        if self.player.voice_client.is_playing() or self.player.voice_client.is_paused():
            self.player.voice_client.stop()
        await self.player.play_next()
        self.update_play_pause_button()
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            pass

    async def stop(self, interaction: discord.Interaction):
        # Обработка нажатия кнопки остановки воспроизведения
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
            else:
                await interaction.followup.send("В данный момент ничего не воспроизводится.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f'Произошла ошибка: {e}', ephemeral=True)

# Ког (расширение) для управления музыкой
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube_api_key = YOUTUBE_API_KEY
        self.players = {}

    def get_player(self, guild):
        # Получение плеера для конкретного сервера
        if guild.id not in self.players:
            self.players[guild.id] = GuildMusicPlayer(self.bot, guild)
        return self.players[guild.id]

    @app_commands.command(name="присоединиться", description="Присоединить Yuuka-chan к голосовому каналу")
    async def join(self, interaction: discord.Interaction):
        # Команда для присоединения бота к голосовому каналу
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("Сенсей, пожалуйста, зайдите в голосовой канал, чтобы Yuuka-chan могла присоединиться.", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        player = self.get_player(interaction.guild)
        await player.connect(channel)
        await interaction.response.send_message("Yuuka-chan к вашим услугам, сенсей", ephemeral=True)

    @app_commands.command(name="отключится", description="Отключить Yuuka-chan от голосового канала")
    async def disconnect(self, interaction: discord.Interaction):
        # Команда для отключения бота от голосового канала
        player = self.get_player(interaction.guild)
        if player.voice_client is not None and player.voice_client.is_connected():
            await player.voice_client.disconnect()
            await interaction.response.send_message("Yuuka-chan больше не подключена к каналу, сенсей", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не подключена к голосовому каналу, сенсей", ephemeral=True)

    @app_commands.command(name="играть", description="Воспроизвести музыку по запросу")
    async def play(self, interaction: discord.Interaction, запрос: str):
        # Команда для воспроизведения музыки
        voice_state = interaction.guild.get_member(interaction.user.id).voice
        if voice_state is None or voice_state.channel is None:
            await interaction.response.send_message("Вы должны быть в голосовом канале, чтобы использовать эту команду.", ephemeral=True)
            return

        player = self.get_player(interaction.guild)
        await player.connect(voice_state.channel)

        await interaction.response.defer(ephemeral=True)

        try:
            # Поиск видео на YouTube по запросу
            if запрос.startswith("http"):
                video_url = запрос
            else:
                results = YoutubeSearch(запрос, max_results=1).to_dict()
                if not results:
                    await interaction.followup.send("По вашему запросу ничего не найдено.", ephemeral=True)
                    return
                video_url = "https://www.youtube.com" + results[0]['url_suffix']

            # Опции для загрузчика YouTube
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'extract_flat': 'in_playlist'
            }

            # Получение информации о видео и URL для потока
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                stream_url = info['url']

            yt = YouTube(video_url)

            # Добавление трека в очередь
            player.add_to_queue(yt, stream_url, interaction)

            # Начало воспроизведения, если плеер не занят
            if not player.voice_client.is_playing():
                player.play()

            await interaction.followup.send(f"{yt.title} добавлен в очередь.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f'Произошла ошибка: {e}', ephemeral=True)

    @app_commands.command(name="плеер", description="Показать текущий плеер")
    async def show_player(self, interaction: discord.Interaction):
        # Команда для отображения текущего состояния плеера
        player = self.get_player(interaction.guild)

        if player.message:
            await interaction.response.send_message("Плеер уже отображается.", ephemeral=True)
        else:
            if player.current:
                yt, _, _ = player.current
                await player.send_now_playing_message(yt)
                await interaction.response.send_message("Плеер отображен.", ephemeral=True)
            else:
                await interaction.response.send_message("Сейчас ничего не воспроизводится.", ephemeral=True)

    @app_commands.command(name="stop", description="Остановить воспроизведение музыки")
    async def stop(self, interaction: discord.Interaction):
        # Команда для остановки воспроизведения музыки
        player = self.get_player(interaction.guild)
        if player.voice_client and player.voice_client.is_playing():
            player.voice_client.stop()
            await interaction.response.send_message("Воспроизведение остановлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="pause", description="Приостановить воспроизведение музыки")
    async def pause(self, interaction: discord.Interaction):
        # Команда для приостановки воспроизведения музыки
        player = self.get_player(interaction.guild)
        if player.voice_client and player.voice_client.is_playing():
            player.voice_client.pause()
            await interaction.response.send_message("Воспроизведение приостановлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="resume", description="Возобновить воспроизведение музыки")
    async def resume(self, interaction: discord.Interaction):
        # Команда для возобновления воспроизведения музыки
        player = self.get_player(interaction.guild)
        if player.voice_client and player.voice_client.is_paused():
            player.voice_client.resume()
            await interaction.response.send_message("Воспроизведение возобновлено, сенсей.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

    @app_commands.command(name="repeat", description="Включить/выключить повтор текущей песни")
    async def repeat(self, interaction: discord.Interaction):
        # Команда для включения/выключения повтора текущего трека
        player = self.get_player(interaction.guild)
        if player.voice_client and player.voice_client.is_playing():
            player.loop = not player.loop
            await interaction.response.send_message(f"Режим повтора {'включен' if player.loop else 'выключен'}.", ephemeral=True)
        else:
            await interaction.response.send_message("Yuuka-chan не воспроизводит музыку, сенсей.", ephemeral=True)

# Функция для добавления кода в бот
async def setup(bot):
    await bot.add_cog(Music(bot))
