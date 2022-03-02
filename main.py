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
client.help_command = None

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
    message = discord.Embed(title = "Not connected to any voice channels.", color=0xea6262)
    message.set_footer(text = "summon me with !join")
    await ctx.send(embed = message)
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
  if url == '':
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
    await print_now_playing(ctx)
    await player_controller(ctx)
    # await ctx.send(embed = message)
  else:
    playlist.append([title, file_name, ctx.author.id, url[-11:]])
    playlist_length = len(playlist) - 1
    member_name = str(ctx.author)
    message = discord.Embed(title = title, color=0x6266ea)
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
    message = discord.Embed(title = "Not connected to any voice channels.", color=0xea6262)
    message.set_footer(text = "summon me with !join")
    await ctx.send(embed = message)
  elif voice_channel.is_playing():
    global playlist
    playlist = []
    voice_channel.stop()

@client.command()
async def skip(ctx):
  global playlist
  if voice_channel is None:
    message = discord.Embed(title = "Not connected to any voice channels.", color=0xea6262)
    message.set_footer(text = "summon me with !join")
    await ctx.send(embed = message)
  else:
    if len(playlist) == 1:
      voice_channel.stop()
      message = discord.Embed(title = "End of queue.", color=0x6266ea)
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
  if voice_channel is None:
    message = discord.Embed(title = "Not connected to any voice channels.", color=0xea6262)
    message.set_footer(text = "summon me with !join")
    await ctx.send(embed = message)
  else:
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
    message = discord.Embed(title = "Not connected to any voice channels.", color=0xea6262)
    message.set_footer(text = "summon me with !join")
    await ctx.send(embed = message)
  else:
    voice_channel.pause()

@client.command()
async def queue(ctx):
  if len(playlist) == 0:
    message = discord.Embed(title = "Not playing", color=0xea6262)
    message.set_footer(text = "play something with !play [Youtube url]")
    await ctx.send(embed = message)
    return
  elif len(playlist) == 1:
    await print_now_playing(ctx)
  else:
    await print_now_playing(ctx)
  # member_name = await ctx.guild.fetch_member(playlist[0][2])
    for i in range(1, len(playlist)):
      song_name = str(playlist[i][0])
      queue_message = discord.Embed(title = song_name, color=0x6266ea)
      member_name = await ctx.guild.fetch_member(playlist[i][2])
      member_name = str(member_name)
      queue_message.add_field(name = str(i) + number(len(playlist) - 1) + " in queue", value=("added by: " + member_name), inline=False)
      queue_message.set_thumbnail(url="https://img.youtube.com/vi/" + playlist[i][3] + "/mqdefault.jpg")
      await ctx.send(embed = queue_message)
  

@client.command()
async def disconnect(ctx):
  global voice_channel
  if voice_channel is not None:
    voice_channel.disconnect()
    voice_channel = None

@client.command()
async def help(ctx):
  message = discord.Embed(title = "Help", color=0x6266ea)
  message.add_field(name = "Join", value = "Summon bot to active voice channel.", inline = False)
  message.add_field(name = "Disconnect", value = "Disconnects bot from active voice channel.", inline = False)
  message.add_field(name = "Play", value = "Play Youtube URL", inline = False)
  message.add_field(name = "Pause", value = "Pauses music playback.", inline = False)
  message.add_field(name = "Resume", value = "Resumes music playback.", inline = False)
  message.add_field(name = "Skip", value = "Skips current song.", inline = False)
  message.add_field(name = "Stop", value = "Stops music playback, clears queue.", inline = False)
  message.add_field(name = "Queue", value = "Brings up queue.", inline = False)
  message.set_thumbnail(url = "https://cdn.discordapp.com/attachments/847111780504698910/872312847944785940/29f9ce2feb6c0d59bd893af9df7c90be.png")
  message.set_footer(text = "\nmade with great pain")
  await ctx.send(embed = message)

async def print_now_playing(ctx):
  member_name = str(ctx.author)
  message = discord.Embed(title = "Now Playing:", color=0x6266ea)
  message.set_thumbnail(url="https://img.youtube.com/vi/" + playlist[0][3] + "/mqdefault.jpg")
  message.add_field(name = playlist[0][0], value = " added by: " + member_name)
  await ctx.send(embed = message)


init()