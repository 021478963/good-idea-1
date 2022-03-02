import discord
import json
from discord.ext import commands
import asyncio

playlist = []
users = []
voice_channel = None

client = commands.Bot(command_prefix="!")

def read_config():
  with open("config.json") as file:
    return json.load(file)

def init():
  config = read_config()
  with open(config["userIDs"]) as file:
    for line in file:
      users.append(line.replace("\n", ""))

  client.run(config["token"])

@client.event
async def on_ready():
  print("ready")

@client.event
async def on_voice_state_update(member, old_voicestate, new_voicestate):
  if voice_channel is None:
    return
  if old_voicestate.channel is voice_channel.channel and len(voice_channel.channel.members) == 1:
    await asyncio.sleep(10)
    if len(voice_channel.channel.members) == 1: # wait 20 seconds and check again
      await disconnect()

async def disconnect():
  global playlist
  await voice_channel.disconnect()
  playlist = []

@client.command()
async def test(ctx):
   await ctx.channel.send("hello")

@client.command()
async def join(ctx):
  vc = ctx.author.voice
  global voice_channel 
  print(voice_channel)
  if (vc == None):
    await ctx.send("Join a voice channel")
  elif voice_channel is None:
    voice_channel = await ctx.author.voice.channel.connect()
  elif not voice_channel.is_connected():
    await voice_channel.disconnect()
    voice_channel = await ctx.author.voice.channel.connect()
  else:
    await ctx.send("Currently busy")

@client.command()
async def play(ctx, url):
  if voice_channel == None or not voice_channel.is_connected():
    await join(ctx)
  if not voice_channel.is_playing():
    voice_channel.play(discord.FFmpegPCMAudio(source=url), after=after_play())
  else:
    playlist.append(url)

def after_play():
  print(playlist)
  



init()