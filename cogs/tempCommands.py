from os import name
from unittest import result
import discord
from Logger import logger
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
import requests
import json

class tempCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    def setup(bot):
        bot.add_cog(tempCommands(bot))


# COMMANDS
    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
        self._last_member = member

    # Custom help command that will be called when !help is called
    @commands.command(name = 'help')
    async def help(self, ctx):

        embed = discord.Embed(title = '**Icarus | Command List** ', description = 'Icarus is a discord bot that is currently in development.', colour = discord.Colour.purple())
        embed.set_thumbnail(url = 'https://cdn-icons-png.flaticon.com/512/1017/1017466.png')
        embed.add_field(name = ':symbols: Command Prefix', value = '```!```',  inline = False)
        # Discord emoji list https://www.webpagefx.com/tools/emoji-cheat-sheet/
        embed.add_field(name = '\U0001F4A1 **General Commands**', value = '```!help```', inline = True)
        embed.add_field(name = ':musical_note: Music Commands', value =  '```!join```' '```!leave```' '```!play <song>```' '```!stop```' '```!resume```' '```!pause```' '```!add```' '```!remove```' '```!clear```', inline = False)
        embed.add_field(name = '\U0001F4A1 **Crypto Tracking**', value = '```!price <ticker>```' '```!priceReminder <ticker> <hours>```' '```!priceReminderStop```' '```!gas```' , inline = False)
        
        # spacing: embed.add_field(name = '\u200b', value = '\u200b', inline = False)
        embed.add_field(name = '\U0001F4A1 **Special Commands**', value = '```!moan```' '```!ping```' '```!meme```' '```!quote```', inline = True)
        await ctx.send(embed = embed)

    
    # Make a ping command
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command(name='quote', description="gets a random quote")
    async def quote(self, ctx):
        quote = requests.get('https://quotable.io/random').json()
        # Prints the quote
        await ctx.send(quote['content'] + ' - ' + quote['author'] + '\n') 
        

    # Create a command that takes in a word and returns the definition of the word and a random example
    @commands.command(name='dictionary', description="gets a random meme")
    async def dictionary(self, ctx, *, word): 
        # Use the best api to get the definition of the word https://api.dictionaryapi.dev/api/v2/entries/en/<word>
        url = 'https://api.dictionaryapi.dev/api/v2/entries/en/' + word
        response = requests.get(url)
        # If the word is not found, it will return a message saying that the word is not found
        if response.status_code == 404:
            await ctx.send('Word not found')
        else:
            # If the word is found, it will return the definition and example
            data = response.json()
            # Gets the first definition
            definition = data[0]['meaning']['noun'][0]['definition']
            # Gets the example
            example = data[0]['meaning']['noun'][0]['example']
            # Prints the definition and example
            await ctx.send(definition + '\n' + example)

    
    # Command that will link a meme image from the below api
    # https://meme-api.herokuapp.com/gimme 
    @commands.command(name='meme', description="links a meme image from the below api")
    async def meme(self, ctx):
        # Gets the player
        member = ctx.author
        api = 'https://meme-api.herokuapp.com/gimme'
        response_json = requests.get(api).json()
        embed = discord.Embed(title="", description="**Heres your random meme:**  " + str(member), color=discord.Color.green())
        #embed.add_field(name="Info:", value='Meme pulled from r/dankmemes', inline=False)
        embed.set_image(url=response_json['url'])
        await ctx.send(embed=embed)
        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction('😊')

# LISTENERS
    # Add a user to a role when they first join the server, and message them hello, inform who they were invited by, and give them the role

    @commands.Cog.listener()
    async def on_member_join(self, ctx, member):
        role = discord.utils.get(member.guild.roles, name='🤦‍♂️ Friendos')
        await ctx.guild.system_channel.send('Welcome {0.mention}.'.format(member))
        await member.add_roles(role)
        await ctx.guild.system_channel.send('{0.mention} was invited by {1.mention}'.format(member, ctx.author))
    # function that will be called when a user leaves the server, bot will print a message onto the discord server that the user has left
    @commands.Cog.listener()
    async def on_member_remove(self, ctx, member):
        print(f'{member} has left the server')
        await ctx.guild.system_channel.send(f'{member} has left the server')


        