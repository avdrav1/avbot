import discord
import json
from discord.ext import commands, tasks
 
from datetime import date
from datetime import timedelta
 
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
 
# Summarise Function
 
def summarize(text, per):
    nlp = spacy.load('en_core_web_sm')
    doc= nlp(text)
    tokens=[token.text for token in doc]
    word_frequencies={}
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency=max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word]=word_frequencies[word]/max_frequency
    sentence_tokens= [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent]=word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent]+=word_frequencies[word.text.lower()]
    select_length=int(len(sentence_tokens)*per)
    summary=nlargest(select_length, sentence_scores,key=sentence_scores.get)
    final_summary=[word.text for word in summary]
    summary=''.join(final_summary)
    print(summary)
    return summary
 
 
# Loading Config
config_file = open("config.json", "r")
config = json.loads(config_file.read())
 
# Creating Client
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=config["prefix"], intents=intents)
 
# Loading
@client.event
async def on_ready():
    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))
 
    #send_ping.start()
 
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
    await ctx.send(f'`JOHN is the only fucking robot here`')   
 
@client.command()
async def toc(ctx):
    await ctx.send(f'`I am the only vagina here`')   

@client.command()
async def virtue(ctx):
    await ctx.send(f'`I will beat your ass in chess and programming`')   


@client.command()
async def crash(ctx):
    await ctx.send(f'`I am a guitar playing Texan.`')   


@client.command()
async def dol(ctx):
    await ctx.send(f'`Shit hit the fan, in America.`')   


@client.command()
async def summary(ctx):
    channel = client.get_channel(ctx.channel.id)
    yesterday = date.today() - timedelta(days = 1)
 
    src_x = []
    async for message in channel.history(limit=20):
        src_x.append("***"+message.author.name + "***" + "\n")
        src_x.append(message.content + "\n")
        #src_x.append(message.jump_url + "\n")
        
 
    await ctx.send(summarize("".join(src_x), 0.25))
 
 
#Tasks
@tasks.loop(minutes=60)
async def send_ping():
    channel = client.get_channel(config["home_channel"])
    await channel.send(f'Pong! In {round(client.latency * 1000)}ms')
 
client.run(config["token"])