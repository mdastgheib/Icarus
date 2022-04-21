#!/usr/bin/env python3
import os
import json
from cogs.tradingCommands import tradingCommands
from cogs.generalCommands import generalCommands
from cogs.MusicCommands import MusicCommands
from cogs.otherCommands import otherCommands
import discord
from Logger import logger
from discord.ext import commands

#
# Loading our config.json: config holds token, api keys, and command prefix
#
with open ('config.json') as config:
    config = json.load(config)
bot = commands.Bot(command_prefix = config["command_prefix"])

#
# Bot initialization class, runs on startup
#
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
            print('\nCurrent Servers logged into:', server.name)
            #await server.system_channel.send('Hey there, ' + server.name + '! Im now online!')

        # Changing the bot's status
        botStatusMessage = discord.Game('!help')
        await bot.change_presence(status = discord.Status.online, activity = botStatusMessage)
        
    # Function that will be called when this specific user sends a specific message in the discord server that the bot is in 
    @bot.event
    async def on_message(message):
        await bot.process_commands(message)

    bot.remove_command('help')
    bot.add_cog(generalCommands(bot))
    bot.add_cog(MusicCommands(bot))
    bot.add_cog(tradingCommands(bot))
    bot.add_cog(otherCommands(bot))

def main():
    try:
        logger.info('Calling bot initialization from main') 
        BotInitialization()

    except Exception as e:
        print(e)
        print("\nThe bot failed to run :(")
        logger.error(e)

main()

