import discord
from discord.ext import commands
import random
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
import youtube_dl
from youtube_dl import YoutubeDL
from Logger import logger

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester
        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.duration = data.get('duration')

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)
        
        # Select first song from a playist (array in this case)
        if 'entries' in data:
            data = data['entries'][0]

        embed = discord.Embed(title="", description=f"Queued [{data['title']}]({data['webpage_url']}) [{ctx.author.mention}]", color=discord.Color.green())
        await ctx.send(embed=embed)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']
        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)



class MusicPlayer:
    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            embed = discord.Embed(title="Now playing", description=f"[{source.title}]({source.web_url}) [{source.requester.mention}]", color=discord.Color.green())
            self.np = await self._channel.send(embed=embed)
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class MusicCommands(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player


    @commands.command(name='join', aliases=['connect', 'j'], description="connects to voice")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = discord.Embed(title="", description="No channel to join. Please call `!join` from a voice channel.", color=discord.Color.green())
                await ctx.send(embed=embed)
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        voiceClient = ctx.voice_client

        if voiceClient:
            if voiceClient.channel.id == channel.id:
                return
            try:
                await voiceClient.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')
        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction('👍')
        await ctx.send(f'**Joined `{channel}`**')



    @commands.command(name='leave', aliases=["stop", "dc", "disconnect", "bye"], description="stops music and disconnects from voice")
    async def leave_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        voiceClient = ctx.voice_client

        if not voiceClient or not voiceClient.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction('👋')
        await ctx.send('**Successfully disconnected**')

        await self.cleanup(ctx.guild)

    # Plays a song via link, search, or ID
    # Utilizing the YTDL library to download and process the audio
    # Parameters
    #  ------------
    #  search: str [Required]

    @commands.command(name='play', aliases=['sing','p'], description="streams music")
    async def play_(self, ctx, *, search: str):
        # Create the player
        await ctx.trigger_typing()
        voiceClient = ctx.voice_client
        # If the bot is not in a voice channel, it will join the channel the user is in
        if not voiceClient:
            await ctx.invoke(self.connect_)
        # If the bot is already in a voice channel, it will leave the current channel and join the new one
        player = self.get_player(ctx)

        # Gets the source via YTDL
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)
        # Call the np command to display the current song
        await player.queue.put(source)


    # Checks if the client is puased, if so, will send a message to the user and pause the music
    # Pauses the currently playing song
    # Parameters
    #  ------------
    #  pause
    @commands.command(name='pause', description="pauses music")
    async def pause_(self, ctx):
        # Gets the player
        voiceClient = ctx.voice_client
        # Checks if the player is playing, if not it will send a message to the user saying that the music is not playing or not connected to a voice channel
        if not voiceClient or not voiceClient.is_playing():
            embed = discord.Embed(title="", description="I am currently not playing anything", color=discord.Color.green())
            await ctx.send(embed=embed)
            return
        # Otherwise it will pause the music
        elif voiceClient.is_paused():
            embed = discord.Embed(title="", description="I am already paused", color=discord.Color.green())
            await ctx.send(embed=embed)
            return
        voiceClient.pause()
        await ctx.send("Paused music ⏸️")



    # Function to resume the music if paused previously
    # Checks if the player is paused, if so it will resume the music
    # Parameters
    #  ------------
    #  resume
    @commands.command(name='resume', description="resumes music")
    async def resume_(self, ctx):

        # Gets the player
        voiceClient = ctx.voice_client
        # Checks if the player is playing, if not it will send a message to the user saying that the music is not playing or not connected to a voice channel
        if not voiceClient or not voiceClient.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)
        # If the player is not pause, it will do nothing and send a message
        elif not voiceClient.is_paused():
            await ctx.send("I am not paused. Use `!pause` to pause the music")
            return
        # If the player is paused, it will resume the music
        voiceClient.resume()
        await ctx.send("Resuming ⏯️")


    # Function to skip the current song
    # Checks if the player is connected, if so, will skip the current song
    # Parameters
    #  ------------
    #  resume
    @commands.command(name='skip', description="skips to next song in queue")
    async def skip_(self, ctx):
        # Gets the player
        voiceClient = ctx.voice_client
        # Checks if the player is playing, if not it will send a message to the user saying that the music is not playing or not connected to a voice channel
        if not voiceClient or not voiceClient.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)
        # If the 
        if voiceClient.is_paused():
            await ctx.send("I am paused. Use `!resume` to resume the music")
            return
        elif not voiceClient.is_playing():
            return

        voiceClient.stop()


    # Function to remove a song from the queue
    # Checks if the player is connected, if so, will remove the current song
    # Parameters
    #  ------------
    #  remove
    @commands.command(name='remove', aliases=['rm', 'rem'], description="removes specified song from queue")
    async def remove_(self, ctx, pos : int=None):
       # Gets the player
        voiceClient = ctx.voice_client
        # Checks if the player is playing, if not it will send a message to the user saying that the music is not playing or not connected to a voice channel
        if not voiceClient or not voiceClient.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        # Gets the player and position of the song
        player = self.get_player(ctx)
        # If the position is not specified, it will remove the current song
        if pos == None:
            player.queue._queue.pop()
        # Otherwise, removes the song at the specified position in the queue and sends a message
        else:
            try:
                song = player.queue._queue[pos-1]
                del player.queue._queue[pos-1]
                embed = discord.Embed(title="", description=f"Removed [{song['title']}]({song['webpage_url']}) [{song['requester'].mention}]", color=discord.Color.green())
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title="", description=f'Could not find a track for "{pos}"', color=discord.Color.green())
                await ctx.send(embed=embed)


    # Function to clear all songs in a queue
    # Checks if the player is connected, if so, will clear the queue
    # Parameters
    #  ------------
    #  clear
    @commands.command(name='clear', aliases=['clr', 'cl', 'cr'], description="clears entire queue")
    async def clear_(self, ctx):

        # Gets the player
        voiceClient = ctx.voice_client
        # Checks if the player is playing, if not it will send a message to the user saying that the music is not playing or not connected to a voice channel
        if not voiceClient or not voiceClient.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        # Gets the player, and clears the queue
        player = self.get_player(ctx)
        player.queue._queue.clear()
        await ctx.send('💣 Cleared the entire queue!')



    # Function to queue 
    # Checks if the player is connected, if so, will clear the queue
    # Parameters
    #  ------------
    #  clear
    @commands.command(name='queue', aliases=['q', 'playlist', 'que'], description="shows the queue")
    async def queue_info(self, ctx):
         # Gets the player
        voiceClient = ctx.voice_client
        # Checks if the player is playing, if not it will send a message to the user saying that the music is not playing or not connected to a voice channel
        if not voiceClient or not voiceClient.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        # Gets the player, checks if the queue is empty, if so, it will send a message saying that the queue is empty
        player = self.get_player(ctx)
        if player.queue.empty():
            embed = discord.Embed(title="", description="queue is empty", color=discord.Color.green())
            return await ctx.send(embed=embed)

        seconds = voiceClient.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        # Grabs the songs in the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))
        fmt = '\n'.join(f"`{(upcoming.index(_)) + 1}.` [{_['title']}]({_['webpage_url']}) | ` {duration} Requested by: {_['requester']}`\n" for _ in upcoming)
        fmt = f"\n__Now Playing__:\n[{voiceClient.source.title}]({voiceClient.source.web_url}) | ` {duration} Requested by: {voiceClient.source.requester}`\n\n__Up Next:__\n" + fmt + f"\n**{len(upcoming)} songs in queue**"
        embed = discord.Embed(title=f'Queue for {ctx.guild.name}', description=fmt, color=discord.Color.green())
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)



    @commands.command(name='np', aliases=['song', 'current', 'currentsong', 'playing'], description="shows the current playing song")
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        voiceClient = ctx.voice_client

        if not voiceClient or not voiceClient.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if not player.current:
            embed = discord.Embed(title="", description="I am currently not playing anything", color=discord.Color.green())
            return await ctx.send(embed=embed)
        
        seconds = voiceClient.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        embed = discord.Embed(title="", description=f"[{voiceClient.source.title}]({voiceClient.source.web_url}) [{voiceClient.source.requester.mention}] | `{duration}`", color=discord.Color.green())
        embed.set_author(icon_url=self.bot.user.avatar_url, name=f"Now Playing 🎶")
        await ctx.send(embed=embed)
