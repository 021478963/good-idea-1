import discord

client = discord.Client()

@client.event
async def on_ready():
  print("we have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if message.content.startswith("!"):
    await message.channel.send("Hello")

if __name__ == "__main__":
  client.run("OTQyMjEwNzk2NzA3MDIwODUx.YghMLw.liWdg6JjaVblbE6mm5A6T9kV63I")