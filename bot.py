#!/usr/bin/env python3

import os
import json
from cogs.CryptoCommands import CryptoCommands
from cogs.tempCommands import tempCommands
from cogs.MusicCommands import MusicCommands
from cogs.reminderCommands import reminderCommands
from cogs.otherCommands import otherCommands
import discord
from Logger import logger
from discord.ext import commands
from discord.ext.commands import Context

# Loading our config.json: config holds token, api keys, and command prefix
with open ('config.json') as config:
    config = json.load(config)

# Initializing our bot and pulling in our prefix from config.json
bot = commands.Bot(command_prefix = config["command_prefix"])

#Class that initializes the bot
class BotInitialization(commands.Bot):
    
    # Initializing our bot pulling in our token from config.json
    def __init__(self):
        bot.run(config["discord_token"])
    
    # Launching bot
    @bot.event
    async def on_ready():
        print('\nThe bot was logged in as: {0.user}'.format(bot)) 
        logger.info('Icarus Bot has started')
        
        for server in bot.guilds:
            print('\nServers logged into:', server.name)
            #await server.system_channel.send('Hey there, ' + server.name + '! Im now online!')

        # Changing the bot's status
        botStatusMessage = discord.Game('!help')
        await bot.change_presence(status = discord.Status.online, activity = botStatusMessage)
        # Overriding the default help command
        
    # Function that will be called when this specific user sends a specific message in the discord server that the bot is in 
    @bot.event
    async def on_message(message):
        # Pass the message to the bot to be processed for commands
        await bot.process_commands(message)

    bot.remove_command('help')
    bot.add_cog(tempCommands(bot))
    bot.add_cog(MusicCommands(bot))
    bot.add_cog(CryptoCommands(bot))
    bot.add_cog(reminderCommands(bot))
    bot.add_cog(otherCommands(bot))

'''
    @bot.command()
    async def load(ctx: Context, extension):
        bot.load_extension(f'cogs.{extension}')
        await ctx.send("Loaded Cog")

    # Create a command that will unload a cog
    @bot.command()
    async def unload(ctx: Context, extension):
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send("Unloaded Cog")

    # Create a command that will reload a cog
    @bot.command()
    async def reload(ctx: Context, extension):
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.send("Reloaded Cog")
    
    # Load cogs from the cogs folder
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
'''
    
def main():
    # Attempt to initialize bot and print error if it fails
    try:
        logger.info('Calling bot initialization from main') 
        BotInitialization()

    except Exception as e:
        print(e)
        print("\nThe bot failed to run :(")
        logger.error(e)

main()

