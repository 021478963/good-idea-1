import discord
import json
from discord.ext import commands
import asyncio
import Get_File

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
   await ctx.send("hello")

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
async def play(ctx, url = ''):
  if voice_channel == None or not voice_channel.is_connected():
    await join(ctx)
  elif url == '':
    voice_channel.resume()
    return

  title, file_name = Get_File.get_title(url)
  Get_File.download_song(file_name, url)
  print("hi")
  print("https://img.youtube.com/vi/" + url[:-11] + "/mqdefault.jpg")
  file_name = "output\\" + file_name

  if not voice_channel.is_playing():
    playlist.append([title, file_name, ctx.author.id])
    voice_channel.play(discord.FFmpegPCMAudio(source = file_name))

    member_name = str(ctx.author)
    message = discord.Embed(title = "Now Playing:")
    message.set_thumbnail(url="https://img.youtube.com/vi/" + url[-11:] + "/mqdefault.jpg")
    message.add_field(name = title, value = " added by: " + member_name)
    await ctx.send(embed = message)
  else:
    playlist.append([title, file_name, ctx.author.id])
    playlist_length = len(playlist) - 1
    member_name = str(ctx.author)
    message = discord.Embed(title = title)
    message_title = str(playlist_length) + number(playlist_length) + " in queue"
    message.add_field(name = message_title, value = "added by: " + member_name)

    await ctx.send(embed = message)
    await player_controller()

def number(playlist_length):
  match playlist_length:
    case 1:
      return "st"
    case 2:
      return "nd"
    case 3:
      return "rd"
    case _:
      return "th"
      

@client.command()
async def stop(ctx):
  if voice_channel is None:
    await ctx.send("Not connected")
  elif voice_channel.is_playing():
    global playlist
    playlist = []
    voice_channel.stop()

@client.command()
async def skip(ctx):
  global playlist
  if voice_channel is None:
    await ctx.send("Not connected")
  else:
    if len(playlist) == 1:
      voice_channel.stop()
    else:
      temp_playlist = playlist
      temp_playlist.pop(0)
      voice_channel.stop()
      playlist = temp_playlist
      print(playlist)
      voice_channel.play(discord.FFmpegPCMAudio(source=playlist[0][1]))

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
      voice_channel.play(discord.FFmpegPCMAudio(source=playlist[0][1]))
    else:
      return

@client.command()
async def pause(ctx):
  if voice_channel is None:
    await ctx.send("Not in channel")
  else:
    voice_channel.pause()

@client.command()
async def queue(ctx):
  if len(playlist) == 0:
    message = discord.Embed(title = "Not playing")
    await ctx.send(embed = message)
    return
  message = discord.Embed(title = "Now Playing")
  queue_message = discord.Embed(title = "Queue")
  member_name = await ctx.guild.fetch_member(playlist[0][2])
  message.add_field(name = playlist[0][0], value=("added by: " + str(member_name)), inline=False)

  for i in range(1, len(playlist)):
    song_name = str(i) + ": " + str(playlist[i][0])
    member_name = await ctx.guild.fetch_member(playlist[i][2])
    member_name = str(member_name)
    queue_message.add_field(name=song_name, value=("added by: " + member_name), inline=False)
  await ctx.send(embed = message)
  await ctx.send(embed = queue_message)

@client.command()
async def disconnect(ctx):
  global voice_channel
  await voice_channel.disconnect()
  voice_channel = None

init()