import discord
from Logger import logger
from discord.ext import commands
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
import os
class tradingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        # Load the config.json file and get the required api keys
        with open('config.json') as config:
            config = json.load(config)
            self.cmc_api_key = config["coinmarketcap_api_key"]
            self.av_api_key = config["alpha_vantage_api_key"]
            

    # 
    # (CMD)
    # Command that gets the current price of a cryptocurrency from the coinmarketcap API
    # Usage: !cPrice <ticker>
    # Utilizes the coinmarketcap API
    # 
    @commands.command(name='cPrice',aliases=['cprice','crypto', 'cryptoPrice', 'cp'], help='Get the price of a cryptocurrency in USD')
    async def cPrice(self, ctx, *, crypto: str):

       # Call the api using our api key in config.json
        api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': crypto,
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.cmc_api_key,
        }

        # Check if the user has specified a cryptocurrency
        if crypto is None:
            await ctx.send("Please specify a cryptocurrency ticker. Example: !price BTC")
            return
        else:
          try:
            response_json = requests.get(api_url, headers=headers, params=parameters).json()
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
            embed = discord.Embed(title=name, description=f'**{symbol} | ${price_usd} USD**'  , colour = discord.Colour.purple())
            embed.add_field(name=':bar_chart: Market Cap', value=f'${market_cap} USD', inline=True)
            embed.add_field(name=':watch: Volume (24h)', value=f'${volume} USD', inline=True)
            embed.add_field(name=':ffig: Circulating Supply', value=f'{circulating_supply}', inline=True)
            embed.add_field(name=':chart_with_upwards_trend: Total Supply', value=f'{total_supply}', inline=True)
            embed.add_field(name=':hourglass: Percent Change (24h)', value=f'{percent_change}%', inline=True)
            embed.set_thumbnail(url='https://cdn-icons.flaticon.com/png/512/4825/premium/4825565.png?token=exp=1649957841~hmac=ce544ffdff393fdfb59b7fa6b73d7d49') 
            embed.set_footer(text='Data provided for educational purposes only.')
            await ctx.send(embed=embed)
          except:
            logger.error("Error sending embed from !cPrice command.")
            await ctx.send("That ticker raised an error, it might not exist or is not on CoinMarketCap. Example: !price BTC")
            return
    
    #
    # (CMD)
    # Command that will find the gas prices of ethereum 
    # Usage: !gas
    # Utilizes ethgasstation.info API
    # 
    @commands.command(name='gas', aliases=['gasPrice'],help='Get the current gwei price of ethereum')
    async def gas(self, ctx):

        # Calling api and getting the data
        api_url = 'https://ethgasstation.info/api/ethgasAPI.json'
        response_json = requests.get(api_url).json()
        low = response_json['safeLow']
        average = response_json['average']
        fast = response_json['fast']
        fastest = response_json['fastest']

        # Format the prices and Divded by 10 to get the gas price in gwei
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
        await ctx.send(embed=embed)

    # 
    # (CMD)
    # Command that gets the current price of a stock using Alpha Vantage API
    # Usage: !sPrice <ticker>
    # Utilzes the alpha vantage API
    # 
    @commands.command(name='sPrice', aliases=['sprice','stock', 'stockPrice', 'sp'],help='Get the price of a stock in USD')
    async def sPrice(self, ctx, ticker):

        api_url = 'https://www.alphavantage.co/query'
        parameters = {
        'function': 'GLOBAL_QUOTE',
        'symbol': ticker,
        'apikey': self.av_api_key,
        'datatype': 'json',
        'outputsize': 'compact'
        }
        headers = {
        'Accepts': 'application/json',
        'AlphaVantagKey': self.av_api_key,
        }
        # Checking if user has specified a ticker
        if ticker is None:
            await ctx.send("Please specify a stock ticker. Example: !sPrice MSFT")
            return
        else:
            try:
                response_json = requests.get(api_url, headers=headers, params=parameters).json()
                symbol = response_json['Global Quote']['01. symbol']
                current_price = response_json['Global Quote']['05. price']
                open_price = response_json['Global Quote']['02. open']
                high_price = response_json['Global Quote']['03. high']
                low_price = response_json['Global Quote']['04. low']
                volume = response_json['Global Quote']['06. volume']
                latest_trading_day = response_json['Global Quote']['07. latest trading day']
                previous_close = response_json['Global Quote']['08. previous close']
                change = response_json['Global Quote']['09. change']
                change_percent = response_json['Global Quote']['10. change percent']

                # Formatting the prices/numbers (Issue with output currently)
                # current_price = '{0:,.3f}'.format(current_price)
                # open_price = '{0:,.3f}'.format(open_price)
                # high_price = '{0:,.3f}'.format(high_price)
                # low_price = '{0:,.3f}'.format(low_price)
                # previous_close = '{0:,.3f}'.format(previous_close)
                # change = '{0:,.3f}'.format(change)
                
                # Embedding data to output to user
                embed = discord.Embed(title=symbol, description=f'**Current Price: ${current_price}**' , colour = discord.Colour.purple())
                embed.add_field(name=":city_sunset: Open Price", value="$" + open_price, inline=True)
                embed.add_field(name=":mailbox_closed: High Price", value="$" + high_price, inline=True)
                embed.add_field(name=":mailbox_with_no_mail: Low Price", value="$" + low_price, inline=True)
                embed.add_field(name=":bar_chart: Volume", value=volume, inline=True)
                embed.add_field(name=":city_dusk: Previous Close", value="$" + previous_close, inline=True)
                embed.add_field(name=":hourglass: Change", value="$" + change, inline=True)
                embed.add_field(name=":hourglass: Percent Change (24h)", value=change_percent, inline=True)
                embed.add_field(name=":cityscape: Latest Trading Day", value=latest_trading_day, inline=True)
                await ctx.send(embed=embed)
            except:
                await ctx.send("Error, unable to process embed with data. Please try again.")
                logger.error("Error sending embed from !sPrice command.")
                return
    
    #    
    # (CMD)
    # Command that converts a currency to another currency
    # Usage: !conversion USD CAD
    # Utilzes the alpha vantage API
    # 
    @commands.command(name='conversion')
    async def conversion(self, ctx, from_currency, to_currency):
        api_url = 'https://www.alphavantage.co/query'
        parameters = {
        'function': 'CURRENCY_EXCHANGE_RATE',
        'from_currency': from_currency,
        'to_currency': to_currency,
        'apikey': self.av_api_key,
        'datatype': 'json',
        'outputsize': 'compact'
        }
        headers = {
        'Accepts': 'application/json',
        'AlphaVantagKey': self.av_api_key,
        }
        # Checking if user has specified a ticker
        if from_currency is None or to_currency is None:
            await ctx.send("Please specify a currency to convert from, and to. Example: !conversion USD EUR ")
            return
        else:
            try:
                response_json = requests.get(api_url, headers=headers, params=parameters).json()
                from_currency = response_json['Realtime Currency Exchange Rate']['1. From_Currency Code']
                to_currency = response_json['Realtime Currency Exchange Rate']['3. To_Currency Code']
                exchange_rate = response_json['Realtime Currency Exchange Rate']['5. Exchange Rate']
                # Embedding data to output to user
                embed = discord.Embed(title=f'{from_currency} to {to_currency}' , colour = discord.Colour.purple())
                embed.add_field(name=":moneybag: Exchange Rate", value=exchange_rate, inline=True)
                await ctx.send(embed=embed)
            except:
                await ctx.send("Error, unable to process embed with data. Please try again.")
                logger.error("Error sending embed from !convert command.")
                return


    #    
    # (CMD)
    # Command that loads in a monthly chart of a stock
    # Usage: !monthly <ticker>
    # Utilzes the alpha vantage API
    # 
    @commands.command(name='monthly', aliases=['m'],help='Get the monthly chart of a stock')
    async def monthly(self, ctx, ticker):
        api_url = "https://www.alphavantage.co/query"
        parameters = {
        'function': 'TIME_SERIES_MONTHLY',
        'symbol': ticker,
        'apikey': self.av_api_key,
        'datatype': 'json',
        'outputsize': 'compact'
        }
        headers = {
        'Accepts': 'application/json',
        'AlphaVantagKey': self.av_api_key,
        }
        # Checking if user has specified a ticker
        if ticker is None:
            await ctx.send("Please specify a stock ticker. Example: !monthly MSFT")
            return
        else:
            try:
                response_json = requests.get(api_url, headers=headers, params=parameters).json()
                symbol = response_json['Meta Data']['2. Symbol']
                data = response_json['Monthly Time Series']
                dates = []
                closing_prices = []
                for date in data:
                    dates.append(date)
                    closing_prices.append(data[date]['4. close'])
                dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
                closing_prices = [float(d) for d in closing_prices]

                # Plot commands
                fig = plt.figure()
                fig = plt.subplot()
                fig.patch.set_facecolor('#d3d3d3')
                fig.plot(dates, closing_prices)
                fig.set_title(symbol + ' Monthly Time Series')
                fig.set_ylabel('Price')
                fig.set_xlabel('Date')
                fig.figure.savefig('monthly.png')

                # Embeddeding the image of the plot, then sending to user and deleting the image from local storage
                embed = discord.Embed(title=symbol + ' Monthly Time Series' , colour = discord.Colour.purple())
                embed.set_image(url='attachment://monthly.png')
                embed.set_footer(text='Requested By: ' + str(ctx.author.name))
                await ctx.send(file=discord.File('monthly.png'), embed=embed)
                os.remove('monthly.png')
            except:
                await ctx.send("Error processing plot data. Please try again. !monthly <ticker>")
                logger.error("Error sending embed from !monthly command.")
                return


    #    
    # (CMD)
    # Command that loads in a weekly chart of a stock
    # Usage: !weekly <ticker>
    # Utilzes the alpha vantage API
    # 
    @commands.command(name='weekly', aliases=['w'],help='Get the weekly chart of a stock')
    async def weekly(self, ctx, ticker):
        api_url = "https://www.alphavantage.co/query"
        parameters = {
        'function': 'TIME_SERIES_WEEKLY',
        'symbol': ticker,
        'apikey': self.av_api_key,
        'datatype': 'json',
        'outputsize': 'compact'
        }
        headers = {
        'Accepts': 'application/json',
        'AlphaVantagKey': self.av_api_key,
        }
        # Checking if user has specified a ticker
        if ticker is None:
            await ctx.send("Please specify a stock ticker. Example: !weekly MSFT")
            return
        else:
            try:
                response_json = requests.get(api_url, headers=headers, params=parameters).json()
                symbol = response_json['Meta Data']['2. Symbol']
                data = response_json['Weekly Time Series']
                dates = []
                closing_prices = []
                for date in data:
                    dates.append(date)
                    closing_prices.append(data[date]['4. close'])
                dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
                closing_prices = [float(d) for d in closing_prices]

                # Plot commands
                fig = plt.figure()
                fig = plt.subplot()
                fig.patch.set_facecolor('#d3d3d3')
                fig.plot(dates, closing_prices)
                fig.set_title(symbol + ' Weekly Time Series')
                fig.set_ylabel('Price')
                fig.set_xlabel('Date')
                fig.figure.savefig('weekly.png')

                # Embeddeding the image of the plot, then sending to user and deleting the image from local storage
                embed = discord.Embed(title=f'{symbol} Weekly Time Series', colour = discord.Colour.purple())
                embed.set_image(url='attachment://weekly.png')
                embed.set_footer(text='Requested By: ' + str(ctx.author.name))
                await ctx.send(file=discord.File('weekly.png'), embed=embed)
                os.remove('weekly.png')
            except:
                await ctx.send("Error processing plot data. Please try again. !weekly <ticker>")
                logger.error("Error sending embed from !weekly command.")
                return
    

    #    
    # (CMD)
    # Command that loads in a daily chart of a stock
    # Usage: !daily <ticker>
    # Utilzes the alpha vantage API
    # 
    @commands.command(name='daily', aliases=['d'],help='Get the daily chart of a stock')
    async def daily(self, ctx, ticker):
        api_url = "https://www.alphavantage.co/query"
        parameters = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker,
        'apikey': self.av_api_key,
        'datatype': 'json',
        'outputsize': 'compact'
        }
        headers = {
        'Accepts': 'application/json',
        'AlphaVantagKey': self.av_api_key,
        }
        # Checking if user has specified a ticker
        if ticker is None:
            await ctx.send("Please specify a stock ticker. Example: !daily MSFT")
            return
        else:
            try:
                response_json = requests.get(api_url, headers=headers, params=parameters).json()
                symbol = response_json['Meta Data']['2. Symbol']
                data = response_json['Time Series (Daily)']
                dates = []
                closing_prices = []
                for date in data:
                    dates.append(date)
                    closing_prices.append(data[date]['4. close'])
                dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
                closing_prices = [float(d) for d in closing_prices]

                # Plot commands
                fig = plt.figure()
                fig = plt.subplot()
                fig.patch.set_facecolor('#d3d3d3')
                fig.plot(dates, closing_prices)
                fig.scatter(dates, closing_prices, color='red', s=8)
                fig.set_title(symbol + ' Daily Time Series')
                fig.set_ylabel('Price')
                fig.set_xlabel('Date')
                fig.figure.savefig('daily.png')

                # Embeddeding the image of the plot, then sending to user and deleting the image from local storage
                embed = discord.Embed(title=f'{symbol} Daily Time Series', colour = discord.Colour.purple())
                embed.set_image(url='attachment://daily.png')
                embed.set_footer(text='Requested By: ' + str(ctx.author.name))
                await ctx.send(file=discord.File('daily.png'), embed=embed)
                os.remove('daily.png')
            except:
                await ctx.send("Error creating the plot data. Please try again. !daily <ticker>")
                logger.error("Error sending embed from !daily command.")
                return


    #    
    # (CMD)
    # Command that loads the cashflow of a stock and displays it in an embed
    # Usage: !cashflow <ticker>
    # Utilzes the alpha vantage API
    # 
    @commands.command(name='cashflow', aliases=['cf'],help='Get the cashflow of a stock')
    async def cashflow(self, ctx, ticker):
        api_url = "https://www.alphavantage.co/query"
        parameters = {
        'function': 'CASH_FLOW',
        'symbol': ticker,
        'apikey': self.av_api_key,
        'datatype': 'json',
        'outputsize': 'compact'
        }
        headers = {
        'Accepts': 'application/json',
        'AlphaVantagKey': self.av_api_key,
        }
        # Checking if user has specified a ticker
        if ticker is None:
            await ctx.send("Please specify a stock ticker. Example: !cashflow MSFT")
            return
        else:
            try:
                response_json = requests.get(api_url, headers=headers, params=parameters).json()
                symbol = response_json['symbol']
                data = response_json['annualReports']
                # Get the most recent yera from the data
                year = data[0]
                fiscalDateEnding = year['fiscalDateEnding']
                operatingCashflow = year['operatingCashflow']
                capitalExpenditures = year['capitalExpenditures']
                cashflowFromInvestment = year['cashflowFromInvestment']
                cashflowFromFinancing = year['cashflowFromFinancing']
                netIncome = year['netIncome']
                dividendPayout = year['dividendPayout']
                profitLoss = year['profitLoss']
                
                # Format the data
                operatingCashflow = '$' + format(float(operatingCashflow), ',')
                profitLoss = '$' + format(float(profitLoss), ',')
                capitalExpenditures = '$' + format(float(capitalExpenditures), ',')
                cashflowFromInvestment = '$' + format(float(cashflowFromInvestment), ',')
                cashflowFromFinancing = '$' + format(float(cashflowFromFinancing), ',')
                netIncome = '$' + format(float(netIncome), ',')
                dividendPayout = dividendPayout.replace(',', '')

                # Embed the data
                embed = discord.Embed(title=f'{symbol} Cash Flow', colour = discord.Colour.purple())
                # Add an image of the company logo to the embed from google
                embed.add_field(name='Fiscal Date Ending', value=fiscalDateEnding, inline=False)
                embed.add_field(name='Net Income', value=netIncome, inline=True)
                embed.add_field(name='Profit Loss', value=profitLoss, inline=True)
                embed.add_field(name='Operating Cash Flow', value=operatingCashflow, inline=True)
                embed.add_field(name='Capital Expenditures', value=capitalExpenditures, inline=True)
                embed.add_field(name='Cashflow From Investment', value=cashflowFromInvestment, inline=True)
                embed.add_field(name='Cashflow From Financing', value=cashflowFromFinancing, inline=True)
                embed.add_field(name='Dividend Payout', value=dividendPayout, inline=False)
                embed.set_footer(text='Requested By: ' + str(ctx.author.name))
                await ctx.send(embed=embed)
            except:
                await ctx.send("Error gathering data. Please try again. !cashflow <ticker>")
                logger.error("Error sending embed from !cashflow command.")
                return


