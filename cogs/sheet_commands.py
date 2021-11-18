import discord
from discord.ext import commands 

import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv

#######
from printer import player_sheet_reader
from character_classes import class_list, barbarian, bard, cleric, druid, fighter, immolator, paladin, ranger, thief, wizard
## both of these imports should be reworked to be class based ie: not floating functions. 

load_dotenv()

URI = os.environ['MONGODB_URI']
cluster = MongoClient(URI)
db = cluster["Roll_bot"]
collection = db["character_sheets"]


class Sheet_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    def check(self, ctx):
        msg = ctx.author
        def inner(msg):
            return msg == ctx.author
        return inner

    # switches 
    # - these switches can maybe be reduced down to a single function which takes another argument for what to grab 

    def class_damage(self, i):
        switch = {
            'barbarian': barbarian['damage'],
            'bard': bard['damage'],
            'cleric': cleric['damage'],
            'druid': druid['damage'],
            'fighter': fighter['damage'],
            'immolator': immolator['damage'],
            'paladin': paladin['damage'],
            'ranger': ranger['damage'],
            'thief': thief['damage'],
            'wizard': wizard['damage'],
        }
        return str(switch.get(i))

    def class_bonds(self, i):
        switch = {
            'barbarian': barbarian['bonds'],
            'bard': bard['bonds'],
            'cleric': cleric['bonds'],
            'druid': druid['bonds'],
            'fighter': fighter['bonds'],
            'immolator': immolator['bonds'],
            'paladin': paladin['bonds'],
            'ranger': ranger['bonds'],
            'thief': thief['bonds'],
            'wizard': wizard['bonds'],
        }
        return switch.get(i)

    def class_hp(self, i):
        switch = {
            'barbarian': barbarian['hp'],
            'bard': bard['hp'],
            'cleric': cleric['hp'],
            'druid': druid['hp'],
            'fighter': fighter['hp'],
            'immolator': immolator['hp'],
            'paladin': paladin['hp'],
            'ranger': ranger['hp'],
            'thief': thief['hp'],
            'wizard': wizard['hp'],
        }
        return switch.get(i)
    
    def class_gear(self, i):
        switch = {
            'barbarian': barbarian["starting-gear"],
            # 'bard': bard["starting-gear"],
            # 'cleric': cleric["starting-gear"],
            # 'druid': druid["starting-gear"],
            # 'fighter': fighter["starting-gear"],
            # 'immolator': immolator["starting-gear"],
            # 'paladin': paladin["starting-gear"],
            # 'ranger': ranger["starting-gear"],
            # 'thief': thief["starting-gear"],
            # 'wizard': wizard["starting-gear"],
        }
        return switch.get(i)
###################################
    @commands.Cog.listener()
    async def on_ready(self):
        print("_____//// Roll bot has loaded sheet_commands ////-----") 

    # C R U D - Create
    @commands.command()
    async def create_char(self,ctx):
        player = ctx.message.author.name
        #check if player has char sheet
            
        if collection.find_one({"player" : player}):
            await ctx.channel.send('You already have a character. If you want to make a new character, you need to delete your current character by typing "/delete-character".')
                
        else:
            player_sheet = {
                "name": '',
                "look": '',
                "class": '',
                "armor": 0,
                "hitpoints": 0, 
                "damage": 0,
                "strength": 0,
                "dexterity": 0,
                "constitution": 0,
                "inteligence": 0,
                "wisdom": 0,
                "charisma": 0,
                "bonds": [],
                "inventory":[]
                }

            starting_stats = ['16','15','13','12', '9', '8']

            await ctx.channel.send('Hello Traveler')
                    
            for i in player_sheet:
                if i == "name":
                    await ctx.channel.send('What is your name ?')
                    name = await self.client.wait_for('message', check=self.check(ctx) )
                    player_sheet["name"] = name.content
                elif i == "look":
                    await ctx.channel.send('Descibe your appearance.')
                    look = await self.client.wait_for('message', check=self.check(ctx)) 
                    player_sheet['look'] = look.content
                elif i == 'armor' or i == "hitpoints" or i == "damage" or i == "bonds" or i == "inventory":
                    pass
                elif i == "class":
                    await ctx.channel.send(f" choose your character's class from this list: {class_list}")

                    valid_ans = False
                    while valid_ans == False:
                        #### this is how we would implement check that we need to test
                        response = await self.client.wait_for('message', check=self.check(ctx)) 

                        if response.content in class_list:
                            player_sheet[i] = response.content
                            print(player_sheet[i])
                            player_sheet['damage'] = self.class_damage(response.content)
                            player_sheet['bonds'] = self.class_bonds(response.content)
                            valid_ans = True
                        else:
                            await ctx.channel.send(f'choose a valid class {class_list}')
                else:
                    await ctx.channel.send(f"choose a value from this list: {starting_stats} to assign to your {i}")

                    valid_ans = False
                    while valid_ans == False:
                        response = await self.client.wait_for('message', check=self.check(ctx))

                        if response.content in starting_stats:
                            starting_stats.pop(starting_stats.index(response.content))
                            player_sheet[i] = response.content
                            valid_ans = True
                        else:
                            await ctx.channel.send(f'choose a valid value {starting_stats}')
            
            player_sheet['hitpoints'] = int(player_sheet['constitution']) + self.class_hp(player_sheet["class"])

            inventory = self.class_gear(player_sheet["class"])

            for i in inventory:
                if type(i) == list:
                    item_check = []
                    base_txt = "choose one of these item: \n ------------ \n "
                    for c in i: 
                        base_txt = base_txt + f" - {c['name']} \n"
                        item_check.append(c["name"])

                    await ctx.channel.send(base_txt)
                    item = await self.client.wait_for("message", check=self.check(ctx))
                    valid_ans = False
                    while valid_ans == False:
                        if item.content in item_check:
                            player_sheet['inventory'].append(i[item_check.index(item.content)])
                            await ctx.channel.send(f"{i[item_check.index(item.content)]['name']} has been added to your inventory")
                            valid_ans = True
                        else:
                            await ctx.channel.send("chose a valid item")
                            item = await self.client.wait_for("message", check=self.check(ctx))
                elif i["info"] == "special-item":

                    await ctx.channel.send(f" Your {i['name']} is {i['prompt']}, describe it.")
                    description = await self.client.wait_for("message", check=self.check(ctx)) 

                    i["description"] = description.content
                    player_sheet["inventory"].append(i)

                else: 
                    player_sheet['inventory'].append(i)
                    await ctx.channel.send(f" { i['name'] } has been added to your inventory")


            # print finished player-sheet
            await ctx.channel.send('player sheet:')

            collection.insert_one({
                "player" : player,      
                "name": player_sheet['name'],
                "look": player_sheet['look'],
                "class": player_sheet["class"],
                "armor": 0,
                "hitpoints": player_sheet['hitpoints'], 
                "damage": player_sheet['damage'],
                "strength": player_sheet['strength'],
                "dexterity": player_sheet['dexterity'],
                "constitution": player_sheet['constitution'],
                "inteligence": player_sheet['inteligence'],
                "wisdom": player_sheet['wisdom'],
                "charisma": player_sheet['charisma'],
                "bonds" : player_sheet['bonds'],
                "inventory": player_sheet["inventory"]
                })

            sheet = collection.find_one({"player" : player})
            await player_sheet_reader(ctx, sheet)
    
    #


    ## Destroy 
    @commands.command()
    async def delete_character(self, ctx):
        player = ctx.message.author
        sheet = collection.find_one({"player": player.name}) # data is just the parsed out bit and deleteing it wont affect the db
        if sheet:
            await ctx.channel.send(f"are you sure you want to delete your character {sheet['name']} - Y / N ")
            answer = await self.client.wait_for('message', check= self.check(ctx)) 
            if answer.content.upper() == 'Y':
                await ctx.channel.send('your character sheet has been destroyed')
                collection.delete_one({"player": player.name})
            else:
                await ctx.channel.send('character not deleted')
                return 

        else:
            await ctx.channel.send('You do not have a player sheet, create one by typing "/create-char" into the chat.')

def setup(client):
    client.add_cog(Sheet_commands(client))

