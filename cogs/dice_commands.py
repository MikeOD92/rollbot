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

    def check(self,ctx):
        def inner(msg):
            return msg.author == ctx.author
        return inner

    @commands.Cog.listener()
    async def on_ready(self):
        print("_____//// Roll bot has loaded dice commands////-----") # on ready should move to main.py

    @commands.command()
    async def hey(self, ctx):
        await ctx.send("Hello it is I Roll_bot") #ping should move to main.py

    @commands.command()
    async def damage(self, ctx):
        player = ctx.author.name

        sheet = collection.find_one({'player': player})
        dice = sheet['damage']

        max = int(dice.split('d', 1)[1])
        rolled = random.randint(1,max)
        rolling_txt = f"... {rolled} "

        await ctx.channel.send(f"{sheet['name']} rolled {dice} for damage \n {rolling_txt} \n do you need to roll additional dice? Y/N")
        answer = await self.client.wait_for('message',  check = self.check(ctx)) 

        if answer.content.upper() == 'Y':
            await ctx.channel.send('roll')
            roll = await self.client.wait_for('message',  check = self.check(ctx))

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
    
    @commands.command()
    async def roll(self, ctx):
        roll = ctx.message.content.split('roll', 1)[1]
        
        sheet = collection.find_one({'player': ctx.author.name})

        if(roll.split('d')[0] == " " or roll.split('d')[0] == "" ):
            num = 1
        else:
            num = int(float(roll.split('d')[0]))

            sides = int(float(roll.split('d')[1]))

            total = 0

            rolls = range(1,num + 1)
            
            rolling_txt = ""

            for n in rolls:
                rolled_num = random.randint(1,sides)
                rolling_txt = rolling_txt + f"... {rolled_num} "
                total = rolled_num + total

            await ctx.channel.send(f"{sheet['name']} rolled {str(roll)} \n {rolling_txt} \n a total of {str(total)}")  
            return total

    @commands.command()
    async def rollplus(self, ctx):
        temp = ctx.message.content.split('rollplus', 1)[1]

        roll = temp.split('+ ')[0]
        attr = temp.split('+ ')[1]

        sheet = collection.find_one({'player': ctx.author.name})

        if(roll.split('d')[0] == " " or roll.split('d')[0] == "" ):
            num = 1
        else:
            num = int(float(roll.split('d')[0]))

            sides = int(float(roll.split('d')[1]))

            total = 0

            rolls = range(1,num + 1)
            
            rolling_txt = ""

            for n in rolls:
                rolled_num = random.randint(1,sides)
                rolling_txt = rolling_txt + f"... {rolled_num} "
                total = rolled_num + total

            if int(sheet[attr]) < 3:
                total -= 3
            elif int(sheet[attr]) <= 5:
                total -= 2
            elif int(sheet[attr]) <= 8:
                total -= 1
            elif int(sheet[attr]) <= 12:
                total = total
            elif int(sheet[attr]) <= 15:
                total += 1
            elif int(sheet[attr]) <= 17:
                total += 2
            elif int(sheet[attr]) > 17:
                total += 3

            await ctx.channel.send(f"{sheet['name']} rolled {str(roll)} \n {rolling_txt} \n and their {attr} modifier makes it a total of {str(total)}")  
            return total + int(sheet[attr]) 


        await ctx.channel.send(f"roll var: {roll} attr var: {attr}")


def setup(client):
    client.add_cog(Dice_commands(client))