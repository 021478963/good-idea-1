import discord
import json
from discord.ext import commands
import asyncio

playlist = []
users = []
voice_channel = None

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

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
async def play(ctx, url = ""):
  if voice_channel == None or not voice_channel.is_connected():
    await join(ctx)
  elif url == '':
    voice_channel.resume()
    return
  if not voice_channel.is_playing():
    playlist.append([url, ctx.author.id])
    voice_channel.play(discord.FFmpegPCMAudio(source=url))
    await ctx.channel.send("Now playing " + url)
  else:
    playlist.append([url, ctx.author.id])
    await player_controller()
      

@client.command()
async def stop(ctx):
  if voice_channel.is_playing():
    voice_channel.stop()

@client.command()
async def pause(ctx):
  if voice_channel.is_playing():
    voice_channel.pause()
  else:
    await ctx.send("Not playing")

@client.command()
async def resume(ctx):
  voice_channel.resume()

async def player():
  while voice_channel.is_playing():
    await asyncio.sleep(1)
  if len(playlist) > 0:
    playlist.pop(0)
  return

async def player_controller():
  while 1:
    await player()
    if len(playlist) > 0:
      voice_channel.play(discord.FFmpegPCMAudio(source=playlist[0][0]))

@client.command()
async def queue(ctx):
  message = discord.Embed(title = "Now Playing")

  member_name = await ctx.guild.fetch_member(playlist[0][1])
  message.add_field(name = playlist[0][0], value=("added by: " + str(member_name)), inline=False)
  message.add_field(name = "Queue", value = "⠀")

  for i in range(1,len(playlist)):
    song_name = str(i) + ": " + str(playlist[i][0])
    member_name = await ctx.guild.fetch_member(playlist[i][1])
    member_name = str(member_name)
    message.add_field(name=song_name, value=("added by: " + member_name), inline=False)
  await ctx.channel.send(embed=message)
    


init()