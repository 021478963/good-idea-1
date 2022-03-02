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
  file_name = "output\\" + file_name

  if not voice_channel.is_playing():
    playlist.append([title, file_name, ctx.author.id, url[-11:]])
    # voice_channel.play(discord.FFmpegPCMAudio(source = file_name))

    # member_name = str(ctx.author)
    # message = discord.Embed(title = "Now Playing:")
    # message.set_thumbnail(url="https://img.youtube.com/vi/" + url[-11:] + "/mqdefault.jpg")
    # message.add_field(name = title, value = " added by: " + member_name)
    await player_controller(ctx)
    # await ctx.send(embed = message)
  else:
    playlist.append([title, file_name, ctx.author.id, url[-11:]])
    playlist_length = len(playlist) - 1
    member_name = str(ctx.author)
    message = discord.Embed(title = title)
    message_title = str(playlist_length) + number(playlist_length) + " in queue"
    message.set_thumbnail(url="https://img.youtube.com/vi/" + url[-11:] + "/mqdefault.jpg")
    message.add_field(name = message_title, value = "added by: " + member_name)

    await ctx.send(embed = message)


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
      message = discord.Embed(title = "End of queue.")
      await ctx.send(embed = message)
    else:
      temp_playlist = playlist
      temp_playlist.pop(0)
      voice_channel.stop()
      playlist = temp_playlist
      voice_channel.play(discord.FFmpegPCMAudio(source=playlist[0][1]))
      await print_now_playing(ctx)

@client.command()
async def resume(ctx):
  voice_channel.resume()

async def player():
  while voice_channel.is_playing():
    await asyncio.sleep(1)
  # if len(playlist) > 0:
  #   playlist.pop(0)
  return

async def player_controller(ctx):
  voice_channel.play(discord.FFmpegPCMAudio(source=playlist[0][1]))
  while 1:
    await player()
    playlist.pop(0)
    if len(playlist) > 0:
      await print_now_playing(ctx)
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
  elif len(playlist) == 1:
    await print_now_playing(ctx)
  else:
    await print_now_playing(ctx)
  # member_name = await ctx.guild.fetch_member(playlist[0][2])
    for i in range(1, len(playlist)):
      song_name = str(playlist[i][0])
      queue_message = discord.Embed(title = song_name)
      member_name = await ctx.guild.fetch_member(playlist[i][2])
      member_name = str(member_name)
      queue_message.add_field(name=str(i) + number(len(playlist) - 1) + " in queue", value=("added by: " + member_name), inline=False)
      queue_message.set_thumbnail(url="https://img.youtube.com/vi/" + playlist[i][3] + "/mqdefault.jpg")
      await ctx.send(embed = queue_message)
  

@client.command()
async def disconnect(ctx):
  global voice_channel
  await voice_channel.disconnect()
  voice_channel = None

async def print_now_playing(ctx):
  member_name = str(ctx.author)
  message = discord.Embed(title = "Now Playing:")
  message.set_thumbnail(url="https://img.youtube.com/vi/" + playlist[0][3] + "/mqdefault.jpg")
  message.add_field(name = playlist[0][0], value = " added by: " + member_name)
  await ctx.send(embed = message)

init()