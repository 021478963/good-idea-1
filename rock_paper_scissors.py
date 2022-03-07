from random import randrange
import discord
import pymongo
import asyncio

client = None

def connect_db(url):
  global client
  try:
    client = pymongo.MongoClient(url)
  except:
    print("Error with MongoDB client")

async def rock_paper_scissors(ctx, option):
  my_input = option.strip().lower()
  random_choice = randrange(0, 3)
  message = discord.Embed()

  '''
    0: rock
    1: paper
    2: scissor
  '''

  match my_input:
    case "rock":
      if random_choice == 0:
        message.title = "It's a tie!"
      elif random_choice == 1:
        message.title = "Better luck next time!"
      else:
        message.title = "Congratulations, you won!"
        update_score(ctx)
    case "paper":
      if random_choice == 0:
        message.title = "Congratulations, you won!"
        update_score(ctx)
      elif random_choice == 1:
        message.title = "It's a tie!"
      else:
        message.title = "Better luck next time!"
    case "scissor":
      if random_choice == 0:
        message.title = "Better luck next time!"
      elif random_choice == 1:
        message.title = "Congratulations, you won!"
        update_score(ctx)
      else:
        message.title = "It's a tie!"
    case _:
      error_message = discord.Embed(title = "You entered an invalid option.")
      error_message.set_footer("please enter rock, paper, or scissors.")
      await ctx.send(embed = error_message)
      return

  await ctx.send(embed = message)
  return

def update_score(ctx):
  user_id = ctx.author.id
  collection = client.rps.scores
  score = collection.find_one({"_id": user_id})
  if score is not None:
    new_score = score["score"] + 1
    collection.update_one({"_id": user_id}, {"$set" : {"score": new_score}})
  else:
    collection.insert_one({"_id": user_id, "score": 1})

async def print_score(ctx):
  collection = client.rps.scores
  message = discord.Embed(title = "Scores:")
  for user in collection.find().sort("score", pymongo.DESCENDING):
    username = await ctx.bot.fetch_user(user["_id"])
    message.add_field(name = username, value = user['score'], inline = False)
  await ctx.send(embed = message)