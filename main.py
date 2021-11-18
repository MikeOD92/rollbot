import discord
import os
from dotenv import load_dotenv

from discord.ext import commands

# intents = discord.Intents.default()
# intents.members = True
# intents.guilds = True
# intents.presences = True
load_dotenv()

client = commands.Bot(command_prefix = '$')

# client = discord.Client()
@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")


token = os.getenv('TOKEN')
client.run(token)

