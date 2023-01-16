import sys
import random
import json
import pytz

from datetime import date
from datetime import timedelta
from datetime import datetime
from pytz import timezone

import discord
import spotipy
import asyncpraw
import pytumblr
import lyricsgenius

from discord.ext import commands, tasks
from discord import app_commands
from tinydb import TinyDB, Query
from obliquestrategies import get_strategy
from quote import quote
from dadjokes import Dadjoke
from newsapi import NewsApiClient
from spotipy.oauth2 import SpotifyClientCredentials
from imgurpython import ImgurClient


# Loading Config
config_file = open("config.json", "r")
config = json.loads(config_file.read())
 
# Creating Discord Client
intents = discord.Intents.all()
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

#Initialize Tumblr
tum = pytumblr.TumblrRestClient(
    config["tumblr_client_id"],
    config["tumblr_client_secret"],
    config["tumblr_token"],
    config["tumblr_token_secret"]
)

#Initialize Lyrics Genius
genius = lyricsgenius.Genius(config['genius_token'])

#Initialize imgur
im = ImgurClient(config['imgur_client_id'], config['imgur_client_secret'])

#Initialize DB
db = TinyDB('avbot.json')
regulars = ['avdrav', 'aya', 'dol', 'robot', 'toc', 'virtue', 'starsmash', 'ina', 'crash', 'quin', 'soupy']

# Loading
@client.event
async def on_ready():
    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))
    
    if not send_strategy.is_running():
        print("Starting Obliques")
        send_strategy.start()
    else:
        print("Oblique already running!") 
 
# Commands

@client.command()
async def ping(ctx):
    await ctx.send(f'`Pong! In {round(client.latency * 1000)}ms`')
 
@client.command()
async def lurk(ctx):
    await ctx.send(f'`We appreciate the lurk!`')

@client.command()
async def listregulars(ctx):
    await ctx.send(regulars)

@client.command()
async def addquote(ctx, name, quote):
    if name in regulars:
        db.insert({'name': name, 'quote': quote })
        await ctx.send(f"{name}'s quote was added!")
    else:
        await ctx.send(f"{name} is not a regular!")

@client.command()
async def getquote(ctx, name):
    if name in regulars:
        Quote = Query()
        results = db.search(Quote.name == name)
        for r in results:
            print(r)
            await ctx.send(f"{r['quote']} - {r['name']}")
    else:
        await ctx.send(f"{name} is not a regular!")

@client.command()
async def oblique(ctx):
    await ctx.send(f'`{get_strategy()}`')   

@client.command()
async def goodreads(ctx, search_arg, limit_arg=1):
    results = quote(search_arg, limit=limit_arg)
    for r in results:
        #print(r)
        goodreads_quote = r["quote"]
        author = r["author"]
        embed=discord.Embed(title=author, description=goodreads_quote)
        await ctx.send(embed=embed)
    
    #await ctx.send(f'```{goodreads_quote}```')
    #await ctx.send(f'***{author}***')
 
@client.command()
async def news(ctx, search_arg, limit_arg):
    top_headlines = newsapi.get_top_headlines(q=search_arg,
                                          sources='bbc-news, abc-news, al-jazeera-english, ars-technica, associated-press, axios, bbc-sport, bloomberg, cbc-news, cbs-news, buzzfeed, cnn, espn, fox-news, fox-sports, google-news, hacker-news, mashable, myv-news, nbc-news, newsweek, politico, reddit-r-all, techcrunch, the-globe-and-mail, the-washington-post, the-wall-street-journal, wired',
                                          language='en')
    print(top_headlines)                                      
    totalResults = top_headlines["totalResults"]
    count = 1
    if totalResults > 0:   
        #await ctx.send(f'Total Headlines: {totalResults}')
        json_headlines = json.loads(json.dumps(top_headlines["articles"]))
        for h in json_headlines:
            print(h)
            await ctx.send(f'```{h["title"]}```{h["url"]}')
            count = count + 1
            if count > limit_arg:
                break
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
async def artist(ctx, artistname="Radiohead"):
    results = sp.search(q='artist:'+artistname, type='artist')
    print(json.dumps(results, indent=4))
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        sp_url = artist['external_urls']['spotify']
        sp_img = artist['images'][0]['url']
        sp_genres = artist['genres']

        embed=discord.Embed(title=artistname, url=sp_url, description=sp_genres)
        embed.set_image(url=sp_img)
        await ctx.send(embed=embed)

@client.command()
async def reddit(ctx, subreddit_arg, sort="top", limit_arg=1):
    
    print("Getting Subreddit: " + subreddit_arg)
    subreddit = await red.subreddit(subreddit_arg, fetch=True)

    print(subreddit.display_name)
    print(subreddit.title)
    print(subreddit.description)

    if sort=="top":
        async for submission in subreddit.top(limit=limit_arg):
            await ctx.send(f'https://reddit.com/{submission.permalink}')
    elif sort=="hot":
        async for submission in subreddit.hot(limit=limit_arg):
            await ctx.send(f'https://reddit.com/{submission.permalink}')
    elif sort=="rising":
        async for submission in subreddit.rising(limit=limit_arg):
            await ctx.send(f'https://reddit.com/{submission.permalink}')
    elif sort=="controversial":
        async for submission in subreddit.controversial(limit=limit_arg):
            await ctx.send(f'https://reddit.com/{submission.permalink}')
    elif sort=="new":
        async for submission in subreddit.new(limit=limit_arg):
            await ctx.send(f'https://reddit.com/{submission.permalink}')
    else:
        await ctx.send(f'Invalid sort: {sort}')
    
@client.command()
async def tumblr(ctx, blog_arg, limit_arg=1):
    blog_info = tum.blog_info(blog_arg)
    #print(json.dumps(blog_info, indent=4))
    total_posts = blog_info['blog']['total_posts']
    posts_json = tum.posts(blog_arg, limit=limit_arg, offset=random.randint(1,total_posts), type="photo")
    #print(json.dumps(posts_json['posts'], indent=4))
    for p in posts_json['posts']:
        #print(json.dumps(p['post_url'], indent=4))
        image_url = p["post_url"].strip('\"')
        await ctx.send(f'{image_url}')

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

@client.command()
async def lyrics(ctx, song_name, artist_name):
    song = genius.search_song(song_name, artist_name)
    #print(song.lyrics)
    #print(len(song.lyrics))
    if len(song.lyrics) <= 2000:
        await ctx.send(f'```{song.lyrics}```')
    else:
        lyrics_chunks = chunkstring(song.lyrics, 1900)
        for chunk in lyrics_chunks:
            #print(chunk)
            #print(len(chunk))
            await ctx.send(f'```{chunk}```')

@client.command()
async def imgur(ctx, query, limit_arg=1):
    total_items = []
    pages = [1,2,3]
    for p in pages:
        items = im.gallery_search(query, page=p)
        for i in items:
            print(i.link)
            total_items.append(i.link)
    print(len(total_items)) 
    if len(total_items) > 0   
        for l in range(0,limit_arg):
            link = random.choice(total_items)
            print(link)
            await ctx.send(link)
    else:
        await ctx.send(f'No Results for: {query}')

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
        sixty_minutes_ago = datetime.now(timezone('UTC')) - timedelta(minutes=60)
        print(last_message_timestamp)
        print(sixty_minutes_ago)
        if last_message_timestamp < sixty_minutes_ago:
            await channel.send(f'`{get_strategy()}`')
 


client.run(config["token"])