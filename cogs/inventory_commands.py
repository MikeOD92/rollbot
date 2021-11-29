import discord
from discord.ext import commands 

import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv

#######
from printer import Printer
from character_classes import Class_info

load_dotenv()

URI = os.environ['MONGODB_URI']
cluster = MongoClient(URI)
db = cluster["Roll_bot"]
inv_collection = db["inventory"]
sheet_collection = db["character_sheets"]


class Inventory_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

#### Switch statement to get class attr info

    def class_switch(self, i, attr):
        classes = Class_info()
        switch = {
            'barbarian': classes.barbarian[attr],
            'bard': classes.bard[attr],
            'cleric': classes.cleric[attr],
            'druid': classes.druid[attr],
            'fighter': classes.fighter[attr],
            'immolator': classes.immolator[attr],
            'paladin': classes.paladin[attr],
            'ranger': classes.ranger[attr],
            'thief': classes.thief[attr],
            'wizard': classes.wizard[attr],
        }
        return (switch.get(i))

###################################
    @commands.Cog.listener()
    async def on_ready(self):
        print("_____//// Roll bot has loaded inventory_commands ////-----") 

    @commands.command()
    async def starting_gear(self, ctx):
        player = ctx.author.name
        player_sheet = sheet_collection.find_one({"player": player})

        inventory = self.class_switch(player_sheet["class"], "starting-gear")

        inv_obj = {
            "player": player,
            "inv_list": []
        }

        for i in inventory:
            if type(i) == list:
                item_check = []
                base_txt = "choose one of these item: \n ------------ \n "
                for c in i: 
                    base_txt = base_txt + f" - {c['name']} \n"
                    item_check.append(c["name"])

                await ctx.channel.send(base_txt)
                item = await self.client.wait_for("message") #, check=self.check(ctx)
                valid_ans = False
                while valid_ans == False:
                    if item.content in item_check:
                        inv_obj["inv_list"].append(i[item_check.index(item.content)])
                        # player_sheet['inventory'].append(i[item_check.index(item.content)])
                        await ctx.channel.send(f"{i[item_check.index(item.content)]['name']} has been added to your inventory")
                        valid_ans = True
                    else:
                        await ctx.channel.send("chose a valid item")
                        item = await self.client.wait_for("message") #, check=self.check(ctx)
                
            elif i["info"] == "special-item":

                await ctx.channel.send(f" Your {i['name']} is {i['prompt']}, describe it.")
                description = await self.client.wait_for("message") #, check=self.check(ctx) 

                i["description"] = description.content
                # player_sheet["inventory"].append(i)# so this needs to chnage to work with the new inventory collection. 
                inv_obj["inv_list"].append(i)
            else: 
                inv_obj["inv_list"].append(i)
                await ctx.channel.send(f" { i['name'] } has been added to your inventory")

        inv_collection.insert_one(inv_obj)

        player_inv = inv_collection.find_one({"player": player})

        printer = Printer()
        
        await printer.inventory_reader(ctx, player_inv)
        
    # $view-items - shows characters inventory
    # @commands.command()
    # async def view_items(self, ctx):
    #     player = ctx.author.name
    #     printer = Printer()

    #     if collection.find_one({"player": player}):
    #         sheet = collection.find_one({"player" : player})
    #         await printer.inventory_reader(ctx, sheet["inventory"])
    #     else:
    #         await ctx.channel.send('You do not have a player sheet, create one by typing "/create-char" into the chat.')
    

def setup(client):
    client.add_cog(Inventory_commands(client))