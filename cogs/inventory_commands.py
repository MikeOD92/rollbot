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
        print("~~~.~.~.~//// Roll bot has loaded inventory_commands ~~~~~.~.~.~//") 

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
                        await ctx.channel.send(f"{i[item_check.index(item.content)]['name']} has been added to your inventory")
                        valid_ans = True
                    else:
                        await ctx.channel.send("chose a valid item")
                        item = await self.client.wait_for("message") #, check=self.check(ctx)
                
            elif i["info"] == "special-item":

                await ctx.channel.send(f" Your {i['name']} is {i['prompt']}, describe it.")
                description = await self.client.wait_for("message") #, check=self.check(ctx) 

                i["description"] = description.content
                inv_obj["inv_list"].append(i)
            else: 
                inv_obj["inv_list"].append(i)
                await ctx.channel.send(f" { i['name'] } has been added to your inventory")

        inv_collection.insert_one(inv_obj)

        player_inv = inv_collection.find_one({"player": player})

        printer = Printer()
        
        await printer.inventory_reader(ctx, player_inv)

    # $view-items - shows characters inventory
    @commands.command()
    async def view_items(self, ctx):
        player = ctx.author.name
        printer = Printer()

        if inv_collection.find_one({"player": player}):
            player_inv = inv_collection.find_one({"player" : player})
            await printer.inventory_reader(ctx, player_inv)
        else:
            await ctx.channel.send('You have not created your characters inventory yet. Type $start_gear into the chat to choose your starting gear.')
    
    # $add_item - allows players to make new items and add them to their inventory
    @commands.command()
    async def add_item(self, ctx):
        player = ctx.author.name
        player_inv = inv_collection.find_one({"player": player})

        new_item = {}

        await ctx.channel.send("what is the name of the item you would like to add to your inventory?")
        name = await self.client.wait_for('message')
        new_item['name'] = name.content

        types = ["weapon", "armor", "gear", "special item"]
        valid_ans = False

        while valid_ans == False:
            await ctx.channel.send("which of the following best describes this item: 'Weapon', 'Armor', 'Gear', or a 'Special item' ")
            info = await self.client.wait_for('message')
            if info.content.lower() in types:
                new_item["info"] = info.content.lower()
                valid_ans = True
            else:
                await ctx.channel.send("select a valid item type.")

        if new_item["info"] == "weapon":
            await ctx.channel.send(" list any attributes this weapon has in a comma seperated list.")
            attr = await self.client.wait_for("message")

            attr_list = attr.content.split(",")
            new_item["attr"] = attr_list

            await ctx.channel.send("what is this weapons damage modifier?")
            damage = await self.client.wait_for("message")

            new_item["damage"] = str(damage.content)

            await ctx.channel.send("what is this weapons weight?")
            weight = await self.client.wait_for("message")

            new_item["weight"] = str(weight.content)
        else:
            print("only weapons work at this time.")

        ### need to flush out questions so we can build items correctly based on type
        player_inv["inv_list"].append(new_item)

        inv_collection.replace_one({"player": player}, player_inv)

    # $drop_item - lists players inventory and asks what item to drop / delete from inventory

    # $encumbered - checks is player is overencumbered or not 


def setup(client):
    client.add_cog(Inventory_commands(client))