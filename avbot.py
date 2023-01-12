import sys
import json
import discord
import spotipy
import asyncpraw


from discord.ext import commands, tasks
 
from datetime import date
from datetime import timedelta
from datetime import datetime
 
from obliquestrategies import get_strategy
from quote import quote
from dadjokes import Dadjoke
from newsapi import NewsApiClient
from spotipy.oauth2 import SpotifyClientCredentials


# Loading Config
config_file = open("config.json", "r")
config = json.loads(config_file.read())
 
# Creating Discord Client
intents = discord.Intents.default()
intents.messages = True
client = commands.Bot(command_prefix=config["prefix"], intents=intents)
 
#Initialize NewsApi
newsapi = NewsApiClient(api_key=config["news_api_key"])

#Initialize Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config["spotipy_client_id"],
                                                           client_secret=config["spotipy_client_secret"]))

#Initialize PRAW (Reddit)
red = asyncpraw.Reddit(
    client_id=config["reddit_client_id"],
    client_secret=config["reddit_client_secret"],
    user_agent="avbot user agent",
)

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
 
@client.command()
async def news(ctx, search_arg):
    top_headlines = newsapi.get_top_headlines(q=search_arg,
                                          sources='bbc-news, abc-news, al-jazeera-english, ars-technica, associated-press, axios, bbc-sport, bloomberg, cbc-news, cbs-news, buzzfeed, cnn, espn, fox-news, fox-sports, google-news, hacker-news, mashable, myv-news, nbc-news, newsweek, politico, reddit-r-all, techcrunch, the-globe-and-mail, the-washington-post, the-wall-street-journal, wired',
                                          language='en')
    print(top_headlines)                                      
    totalResults = top_headlines["totalResults"]
    if totalResults > 0:   
        await ctx.send(f'Total Headlines: {totalResults}')
        json_headlines = json.loads(json.dumps(top_headlines["articles"]))
        for h in json_headlines:
            print(h)
            await ctx.send(f'```{h["title"]}```{h["url"]}')
    else:
        await ctx.send(f"No headlines found for {search_arg}")

@client.command()
async def newssources(ctx):
    sources = newsapi.get_sources()
    json_sources = json.loads(json.dumps(sources["sources"]))
    #print (json_sources)
    for s in json_sources:
        print(s["id"])

@client.command()
async def joke(ctx):
    dadjoke = Dadjoke()
    await ctx.send(f'```{dadjoke.joke}```')

@client.command()
async def artist(ctx, artistname):
    if artistname is None:
        artistname = "Radiohead"
    else:
        pass

    results = sp.search(q='artist:'+artistname, type='artist')
    print(results)
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        await ctx.send(f"{artist['images'][0]['url']}")

@client.command()
async def reddit(ctx, subreddit_arg):
    subreddit = await red.subreddit(subreddit_arg, fetch=True)

    #print(subreddit.display_name)
    #print(subreddit.title)
    #print(subreddit.description)
    
    async for submission in subreddit.top(limit=3):
        #print(submission.title)
        #print(submission.score)
        #print(submission.id)
        await ctx.send(f'https://reddit.com/{submission.permalink}')
    

#Tasks
@tasks.loop(minutes=60)
async def send_ping():
    channel = client.get_channel(config["home_channel"])
    await channel.send(f'Pong! In {round(client.latency * 1000)}ms')

@tasks.loop(seconds=60)
async def send_strategy():
    channel = client.get_channel(config["home_channel"])
    async for message in channel.history(limit=1):
        last_message_timestamp = message.created_at
        sixty_minutes_ago = datetime.now() - timedelta(minutes=60)
        if last_message_timestamp < sixty_minutes_ago:
            await channel.send(f'`{get_strategy()}`')
 


client.run(config["token"])