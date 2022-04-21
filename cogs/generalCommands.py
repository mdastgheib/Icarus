import discord
from Logger import logger
from discord.ext import commands
import random
import requests

class generalCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    #
    # (CMD)
    # - Help Command (Sends a list of commands to user inside an embed)
    #
    @commands.command(name = 'help')
    async def help(self, ctx):
        embed = discord.Embed(title = '**Icarus | Command List** ', description = 'Icarus is a discord bot that is currently in development.', colour = discord.Colour.purple())
        embed.set_thumbnail(url = 'https://cdn-icons-png.flaticon.com/512/1017/1017466.png')
        embed.add_field(name = ':symbols: Command Prefix', value = '```!```',  inline = False)
        embed.add_field(name = '\U0001F4A1 **General Commands**', value = '```!help```', inline = False)
        embed.add_field(name = ':musical_note: Music Commands', value =  '```!join```' '```!leave```' '```!play <song>```' '```!stop```' '```!resume```' '```!pause```' '```!add```' '```!remove```' '```!clear```', inline = True)
        embed.add_field(name = '\U0001F4A1 **Crypto Tracking**', value = '```!cPrice <ticker>```' '```!gas```' , inline = False)
        embed.add_field(name = '\U0001F4A1 **Stock Tracking**', value = '```!sPrice <ticker>```' , inline = False)
        embed.add_field(name = '\U0001F4A1 **Special Commands**', value = '```!conversion <currency> <currency>```' '```!poll <question>, <option1>, <option2>```' '```!ping```' '```!meme```' '```!quote```', inline = True)
        await ctx.send(embed = embed)

    #
    # (CMD)
    # - Hello Command (Says hello to the user)
    #
    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
        self._last_member = member
    
    #
    # (CMD)
    # - Ping Command (Replies with Pong)
    #
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    #
    # (CMD)
    # - Quote Command (Returns a random quote from the quotable.io API)
    #
    @commands.command(name='quote', description="gets a random quote")
    async def quote(self, ctx):
        quote = requests.get('https://quotable.io/random').json()
        await ctx.send(quote['content'] + ' - ' + quote['author'] + '\n') 
    #   
    # (CMD)
    # - Meme Command (Replies with a random meme from the meme-api.herokuapp.com API)
    #
    @commands.command(name='meme', description="links a meme image from the below api")
    async def meme(self, ctx):
        member = ctx.author
        api = 'https://meme-api.herokuapp.com/gimme'
        response_json = requests.get(api).json()
        embed = discord.Embed(title="", description="**Heres your random meme:**  " + str(member), color=discord.Color.green())
        embed.set_image(url=response_json['url'])
        embed.set_footer(text="Memes pulled from r/dankmemes")
        await ctx.send(embed=embed)
        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction('😊')


    #
    # (CMD)
    # - Poll Command (Allows a user to create a poll via reactions)
    #
    @commands.command(name='poll', description="Creates a poll")
    async def poll(self, ctx, *options: str):
        options_list = options
        options_list = ' '.join(options_list)
        options_list = options_list.split(',')
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        # Check if there are enough options, minimum 2
        if len(options) < 3:
            await ctx.send('```You need more than one option to make a poll, try !poll <question>, <option1>, <option2> ...```')
            return
        elif len(options) > 11:
            await ctx.send('```You can only make a poll with a maximum of 10 options, try !poll <question> <option1> <option2> ...```')
            return
        else:
            embed = discord.Embed(title=options_list[0], description='React with the corresponding number to vote!', color=discord.Color.purple())
            for i in range(1, len(options_list)):
                embed.add_field(name=reactions[i-1], value=options_list[i])
            embed.set_footer(text='Poll created by ' + str(ctx.author.name))
            msg = await ctx.send(embed=embed)
            for reaction in reactions[:len(options_list)-1]:
                await msg.add_reaction(reaction)

    #
    # (LISTENER)
    # - On join listener, sends a message to the channel when a user joins
    # 
    @commands.Cog.listener()
    async def on_member_join(self, ctx, member):
        role = discord.utils.get(member.guild.roles, name='🤦‍♂️ Friendos')
        logger.info(f'{member} has joined the server')
        await ctx.guild.system_channel.send('Welcome {0.mention}.'.format(member))
        await member.add_roles(role)
        await ctx.guild.system_channel.send('{0.mention} was invited by {1.mention}'.format(member, ctx.author))

    #
    # (LISTENER)
    # - On leave listener, sends a message to the channel when a user leaves
    # 
    @commands.Cog.listener()
    async def on_member_remove(self, ctx, member):
        print(f'{member} has left the server')
        logger.info(f'{member} has left the server')
        await ctx.guild.system_channel.send(f'{member} has left the server')


        