import discord
import json
from discord.ext import commands, tasks
 
from datetime import date
from datetime import timedelta
from datetime import datetime
 
from obliquestrategies import get_strategy
from quote import quote

# Loading Config
config_file = open("config.json", "r")
config = json.loads(config_file.read())
 
# Creating Client
intents = discord.Intents.default()
intents.messages = True
client = commands.Bot(command_prefix=config["prefix"], intents=intents)
 
# Loading
@client.event
async def on_ready():
    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))
 
    if not send_strategy.is_running():
        send_strategy.start() 
 
# Commands
@client.command()
async def ping(ctx):
    await ctx.send(f'`Pong! In {round(client.latency * 1000)}ms`')
 
@client.command()
async def lurk(ctx):
    await ctx.send(f'`We appreciate the lurk!`')

@client.command()
async def aya(ctx):
    await ctx.send(f'`MIQ is AOTY`')
    await ctx.send(f'`Youre a beautiful genius and if you tried at all, its perfect.`')    

@client.command()
async def robot(ctx):
    await ctx.send(f'`JOHN is the only fucking robot here.`')   
 
@client.command()
async def toc(ctx):
    await ctx.send(f'`I say this with my full chest and both titties.`')   

@client.command()
async def virtue(ctx):
    await ctx.send(f'`Can you please stop playing chess with my dad?  Its disgusting!`')   

@client.command()
async def starsmash(ctx):
    await ctx.send(f'`I will review the fuck out of you -- keep creating!`')   

@client.command()
async def ina(ctx):
    await ctx.send(f'`Tall, Finnish, and sad.`')   
    await ctx.send(f'`Check #content-dumping for my latest contributions!`')   

@client.command()
async def crash(ctx):
    await ctx.send(f'`I am a guitar playing Texan.`')   

@client.command()
async def dol(ctx):
    await ctx.send(f'`Shit hit the fan, in America.`')   

@client.command()
async def quin(ctx):
    await ctx.send(f'`The mighty eskimo!`')   

@client.command()
async def oblique(ctx):
    await ctx.send(f'`{get_strategy()}`')   

@client.command()
async def goodreads(ctx, search_arg):
    result = quote(search_arg, limit=1)
    json_quote = json.loads(json.dumps(result[0]))
    goodreads_quote = json_quote["quote"]
    author = json_quote["author"]
    await ctx.send(f'```{goodreads_quote}```')
    await ctx.send(f'***{author}***')
 
#Tasks
@tasks.loop(minutes=60)
async def send_ping():
    channel = client.get_channel(config["home_channel"])
    await channel.send(f'Pong! In {round(client.latency * 1000)}ms')

@tasks.loop(seconds=60)
async def send_strategy():
    channel = client.get_channel(config["home_channel"])
    last_message = []
    async for message in channel.history(limit=1):
        last_message_timestamp = message.created_at
        sixty_minutes_ago = datetime.now() - timedelta(minutes=60)
        if last_message_timestamp < sixty_minutes_ago:
            await channel.send(f'`{get_strategy()}`')
 


client.run(config["token"])