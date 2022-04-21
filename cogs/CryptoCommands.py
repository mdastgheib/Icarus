import datetime
from os import name
import discord
from Logger import logger
from discord.ext import commands
import requests
import json
import io
import asyncio
import mysql
import mysql.connector

class CryptoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        # Load the config.json file and get the coinmarketcap api key
        with open('config.json') as config:
            config = json.load(config)
            self.api_key = config["coinmarketcap_api_key"]
            
            # Database load
            self.db_host = config["db_host"]
            self.db_user = config["db_user"]
            self.db_password = config["db_password"]
            self.db_name = config["db_name"]
            self.db_port = config["db_port"]

#  Using the coinmarketcap API to get the current price of a cryptocurrency in USD
    @commands.command(name='price', help='Get the price of a cryptocurrency in USD')
    async def price(self, ctx, *, crypto: str):

       # Call the api using our api key in config.json
        api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': crypto,
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }

        # Check if the user has specified a cryptocurrency
        if crypto is None:
            await ctx.send("Please specify a cryptocurrency ticker. Example: !price BTC")
            return
        else:
          try:
              # Make the request from user input, get the ticker symbol, and the price in USD
            response_json = requests.get(api_url, headers=headers, params=parameters).json()
            # Below is the information we want to display from the response, parsed from json
            price_usd = response_json['data'][crypto]['quote']['USD']['price']
            name = response_json['data'][crypto]['name']
            symbol = response_json['data'][crypto]['symbol']
            market_cap = response_json['data'][crypto]['quote']['USD']['market_cap']
            volume = response_json['data'][crypto]['quote']['USD']['volume_24h']
            circulating_supply = response_json['data'][crypto]['circulating_supply']
            total_supply = response_json['data'][crypto]['total_supply']
            percent_change = response_json['data'][crypto]['quote']['USD']['percent_change_24h']
          
            # Format the prices and numbers
            price_usd = '{0:,.3f}'.format(price_usd)
            market_cap = '{0:,.2f}'.format(market_cap)
            volume = '{0:,.2f}'.format(volume)
            circulating_supply = '{0:,.1f}'.format(circulating_supply)
            total_supply = '{0:,.1f}'.format(total_supply)
            percent_change = '{0:,.2f}'.format(percent_change)
            
            # Embed the data
            embed = discord.Embed(title=name, description=f'**{symbol} | ${price_usd} USD**'  , color=0x00ff00)
            embed.add_field(name=':bar_chart:Market Cap', value=f'${market_cap} USD', inline=True)
            embed.add_field(name=':watch: Volume (24h)', value=f'${volume} USD', inline=True)
            embed.add_field(name=':fax: Circulating Supply', value=f'{circulating_supply}', inline=True)
            embed.add_field(name=':chart_with_upwards_trend: Total Supply', value=f'{total_supply}', inline=True)
            embed.add_field(name=':hourglass: Percent Change (24h)', value=f'{percent_change}%', inline=True)
            embed.set_thumbnail(url='https://cdn-icons.flaticon.com/png/512/4825/premium/4825565.png?token=exp=1649957841~hmac=ce544ffdff393fdfb59b7fa6b73d7d49') 
            await ctx.send(embed=embed)
          except:
            await ctx.send("That ticker raised an error, it might not exist or is not on CoinMarketCap. Example: !price BTC")
            return
    

    # Command that will find the gas prices of ethereum from the following api
    # https://ethgasstation.info/api/ethgasAPI.json?
    @commands.command()
    async def gas(self, ctx):
        # Get the gas prices from the api
        api_url = 'https://ethgasstation.info/api/ethgasAPI.json'
        response_json = requests.get(api_url).json()
        # Get the gas prices from the response
        low = response_json['safeLow']
        average = response_json['average']
        fast = response_json['fast']
        fastest = response_json['fastest']
        # Format the prices
        # Divded by 10 to get the gas price in gwei
        low = '{0:,.0f}'.format(low/10)
        average = '{0:,.0f}'.format(average/10)
        fast = '{0:,.0f}'.format(fast/10)
        fastest = '{0:,.0f}'.format(fastest/10)

        # Embed the data
        embed = discord.Embed(title=':fuelpump: Current ETH Gas Prices', color=0x00ff00)
        embed.add_field(name=':turtle: | Slow ( > 10 minutes )', value=f'{low} Gwei', inline=False)
        embed.add_field(name=':person_walking: | Average ( < 5 minutes ) ', value=f'{average} Gwei', inline=False)
        embed.add_field(name=':fire: | Fast ( < 30 seconds )', value=f'{fast} Gwei', inline=False)
        embed.add_field(name=':zap: | Fastest ( < 15 seconds )', value=f'{fastest} Gwei', inline=False)
        # Send the embd privately to the user
        await ctx.send(embed=embed)

    '''
# Logic:
- Convert the interval to a timer, and store the time
- Would we store the time as a timer or should we store it with current time and add the interval to it?
- Check if the time is up every 3 minuntes
- If the time is up, send the user a message for each ticker from the ticker tables
- Update the time again with the interval set from the database
'''
    
    # Create a command that stores the users ID and will send them a message on a defined interval interval, this is used to remind users of their daily price in USD
    # Store this in a database so that the bot can read it and send the user a message on their desired interval interval
    @commands.command(name='priceReminder', help='Store the users ID and send them a message on a defined interval interval')
    async def priceReminder(self, ctx, crypto : str, interval : int):
        # Check if the user has specified a cryptocurrency
        if interval is None:
            await ctx.send("Please specify an interval in hours. Example: !priceReminderStore BTC INTERVAL")
            return
        # Send the user a message with the interval
        # Connect to the database
        # Convert interval to an int
        #interval = int(interval)
        conn = mysql.connector.connect(user=self.db_user, password=self.db_password, host=self.db_host, database=self.db_name)
        cursor = conn.cursor()

        # Call the api using our api key in config.json
        api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': crypto,
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }

        # Check if the user is already in the database
        cursor.execute(f"SELECT * FROM Users WHERE USERID = {ctx.author.id}")
        result = cursor.fetchall()

        # Get the current time and add the interval to it as hours (Below is example of 3 interval)
        # 2022-04-15 17:05:16.239126
        # 2022-04-15 20:05:16.239126
        current_time = datetime.datetime.now()
        intervalTime = current_time + datetime.timedelta(hours=interval)
        # Only let the time have 2 digits after the decimal
        intervalTime = intervalTime.strftime("%Y-%m-%d %H:%M:%S.%f")
        intervalTime = intervalTime[:-4]

        # If the user is not in the database, add them
        if not result:
            cursor.execute(f"INSERT INTO Users (USERID, intervalSelected, intervalTime) VALUES ({ctx.author.id}, {interval}, '{intervalTime}')")
            conn.commit()
            await ctx.send(f'{ctx.author.mention} You will be sent a message with price updates for that {crypto} every {interval} hours. To stop all messages, type !priceReminderStop')
        # If the user is already in the database, update their interval
        else:
            # Update the interval for the user int he database
            cursor.execute(f"UPDATE Users SET intervalSelected = '{interval}', intervalTime = '{intervalTime}' WHERE USERID = '{ctx.author.id}'")
            conn.commit()
            await ctx.send(f'{ctx.author.mention} Your interval has been updated to {interval} hours.')

        # Check if the user has specified a cryptocurrency
        if crypto is None:
            await ctx.send("Please specify a cryptocurrency ticker. Example: !price BTC (hours)")
            return
        else:
          try:
            # Insert a new entry into the table called 'Tickers', this will store the USERID and Ticker symbol
            cursor.execute(f"INSERT INTO Tickers (USERID, Ticker) VALUES ({ctx.author.id}, '{crypto}')")
            cursor.close()
            conn.close()

            # Message the user with the embed that contains all the price data, similar to the above commands
            # Get the data from the API
            # Make the request from user input, get the ticker symbol, and the price in USD
            response_json = requests.get(api_url, headers=headers, params=parameters).json()
            # Below is the information we want to display from the response, parsed from json
            price_usd = response_json['data'][crypto]['quote']['USD']['price']
            name = response_json['data'][crypto]['name']
            symbol = response_json['data'][crypto]['symbol']
            market_cap = response_json['data'][crypto]['quote']['USD']['market_cap']
            volume = response_json['data'][crypto]['quote']['USD']['volume_24h']
            circulating_supply = response_json['data'][crypto]['circulating_supply']
            total_supply = response_json['data'][crypto]['total_supply']
            percent_change = response_json['data'][crypto]['quote']['USD']['percent_change_24h']
          
            # Format the prices and numbers
            price_usd = '{0:,.3f}'.format(price_usd)
            market_cap = '{0:,.2f}'.format(market_cap)
            volume = '{0:,.2f}'.format(volume)
            circulating_supply = '{0:,.1f}'.format(circulating_supply)
            total_supply = '{0:,.1f}'.format(total_supply)
            percent_change = '{0:,.2f}'.format(percent_change)
            
            # Embed the data
            embed = discord.Embed(title=name, description=f'**{symbol} | ${price_usd} USD**'  , color=0x00ff00)
            embed.add_field(name=':bar_chart:Market Cap', value=f'${market_cap} USD', inline=True)
            embed.add_field(name=':watch: Volume (24h)', value=f'${volume} USD', inline=True)
            embed.add_field(name=':fax: Circulating Supply', value=f'{circulating_supply}', inline=True)
            embed.add_field(name=':chart_with_upwards_trend: Total Supply', value=f'{total_supply}', inline=True)
            embed.add_field(name=':hourglass: Percent Change (24h)', value=f'{percent_change}%', inline=True)
            embed.set_thumbnail(url='https://cdn-icons.flaticon.com/png/512/4825/premium/4825565.png?token=exp=1649957841~hmac=ce544ffdff393fdfb59b7fa6b73d7d49') 
            # Send the embd privately to the user
            await ctx.author.send(embed=embed)
            return
          except:
            await ctx.send("That ticker raised an error, it might not exist or is not on CoinMarketCap. Example: !priceReminder ticker hours")
            return
        # Close the connection
        

    # Create a command that will stop the price reminder and delete the user from the database
    @commands.command(name='priceReminderStop', help='Stops the price reminder for the user')
    async def priceReminderStop(self, ctx):
        # Connect to the database
        conn = mysql.connector.connect(user=self.db_user, password=self.db_password, host=self.db_host, database=self.db_name)
        cursor = conn.cursor()

        # Check if the user is already in the database
        cursor.execute(f"SELECT * FROM Users WHERE USERID = {ctx.author.id}")
        result = cursor.fetchall()

        # If the user is not in the database, send a message saying they are not in the database
        if not result:
            await ctx.send(f'{ctx.author.mention} You are not in the database.')
            return
        # If the user is in the database, delete them from the database
        else:
            cursor.execute(f"DELETE FROM Users WHERE USERID = {ctx.author.id}")
            cursor.execute(f"DELETE FROM Tickers WHERE USERID = {ctx.author.id}")
            conn.commit()
            await ctx.send(f'{ctx.author.mention} You have been removed from the database.')
            return
        # Close the connection
    # Create a listener that checks every 3 minutes.
    # This listener will check if the user's time matches the current time, and if so, it will message the user the prices from the tickers table
    # Then, it will update the time in the database to the current time + the interval from the database
    @commands.Cog.listener()
    async def on_ready(self):
        # Connect to the database
        conn = mysql.connector.connect(user=self.db_user, password=self.db_password, host=self.db_host, database=self.db_name)
        cursor = conn.cursor()
        # Check if the user is already in the database
        cursor.execute(f"SELECT * FROM Users")
        result = cursor.fetchall()

        # Get the current time
        current_time = datetime.datetime.now(datetime.timezone.utc).astimezone().replace(tzinfo=None) 
        # Loop through the database and check if the time matches the current time
        
        print(current_time)
        current_time = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        current_time = current_time[:-4]
        # covnert the current time to a datetime object
        current_time = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S.%f")


        # Loop through the database and check if the time is up
        for user in result:
            print((f'{user[0]}, {user[1]}, {user[2]}'))
            print(current_time)
            # Check if the time is within the interval of the user
            if current_time >= user[2]:
                # Get the tickers from the database
                cursor.execute(f"SELECT * FROM Tickers WHERE USERID = {user[0]}")
                tickers = cursor.fetchall()
                updated_time = current_time + datetime.timedelta(hours=user[1])
                # Update the time in the Users table, add the interval to the current time to get the new time
                cursor.execute(f"UPDATE Users SET intervalTime = {updated_time} WHERE USERID = {user[0]}")
                # Loop through the tickers and get the price for each one
                for ticker in tickers:
                    # Get the price for each ticker
                    # Call the api using our api key in config.json
                    api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
                    parameters = {
                        'symbol': ticker[1],
                        'convert': 'USD'
                    }
                    headers = {
                        'Accepts': 'application/json',
                        'X-CMC_PRO_API_KEY': self.api_key,
                    }


                    response_json = requests.get(api_url, headers=headers, params=parameters).json()
                    # Below is the information we want to display from the response, parsed from json
                    price_usd = response_json['data'][ticker[1]]['quote']['USD']['price']
                    name = response_json['data'][ticker[1]]['name']
                    symbol = response_json['data'][ticker[1]]['symbol']
                    market_cap = response_json['data'][ticker[1]]['quote']['USD']['market_cap']
                    volume = response_json['data'][ticker[1]]['quote']['USD']['volume_24h']
                    circulating_supply = response_json['data'][ticker[1]]['circulating_supply']
                    total_supply = response_json['data'][ticker[1]]['total_supply']
                    percent_change = response_json['data'][ticker[1]]['quote']['USD']['percent_change_24h']
                
                    # Format the prices and numbers
                    price_usd = '{0:,.3f}'.format(price_usd)
                    market_cap = '{0:,.2f}'.format(market_cap)
                    volume = '{0:,.2f}'.format(volume)
                    circulating_supply = '{0:,.1f}'.format(circulating_supply)
                    total_supply = '{0:,.1f}'.format(total_supply)
                    percent_change = '{0:,.2f}'.format(percent_change)
                    
                    # Embed the data
                    embed = discord.Embed(title=name, description=f'**{symbol} | ${price_usd} USD**'  , color=0x00ff00)
                    embed.add_field(name=':bar_chart:Market Cap', value=f'${market_cap} USD', inline=True)
                    embed.add_field(name=':watch: Volume (24h)', value=f'${volume} USD', inline=True)
                    embed.add_field(name=':fax: Circulating Supply', value=f'{circulating_supply}', inline=True)
                    embed.add_field(name=':chart_with_upwards_trend: Total Supply', value=f'{total_supply}', inline=True)
                    embed.add_field(name=':hourglass: Percent Change (24h)', value=f'{percent_change}%', inline=True)
                    embed.set_thumbnail(url='https://cdn-icons.flaticon.com/png/512/4825/premium/4825565.png?token=exp=1649957841~hmac=ce544ffdff393fdfb59b7fa6b73d7d49') 
                    # Send the embd privately to the user
                    await self.bot.get_user(user[0]).send(embed=embed)



