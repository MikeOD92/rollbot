import discord
from discord.ext import commands 

import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

URI = os.environ['MONGODB_URI']
cluster = MongoClient(URI)
db = cluster["Roll_bot"]
collection = db["character_sheets"]

class Dice_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("_____ Roll bot is Online -----")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("pong")

    @commands.command()
    async def damage(self, ctx):
        player = ctx.author.name

        sheet = collection.find_one({'player': player})
        dice = sheet['damage']

        max = int(dice.split('d', 1)[1])
        rolled = random.randint(1,max)
        rolling_txt = f"... {rolled} "

        await ctx.channel.send(f"{sheet['name']} rolled {dice} for damage \n {rolling_txt} \n do you need to roll additional dice? Y/N")
        answer = await self.client.wait_for('message')

        if answer.content.upper() == 'Y':
            await ctx.channel.send('roll')
            roll = await self.client.wait_for('message')

            num = int(float(roll.content.split('d')[0]))
            sides = int(float(roll.content.split('d')[1]))

            rolling_text = ""
                
            for n in range(num):
                roll = random.randint(1,sides)
                rolled += roll
                rolling_text += f"... {roll}"
                    
            await ctx.channel.send(f"{rolling_text} \n {sheet['name']} did {rolled} damage")

        else:
            return 


def setup(client):
    client.add_cog(Dice_commands(client))