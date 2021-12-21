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
collection = db["character_sheets"]
inv_collection = db["inventory"]

class Sheet_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    def check(self, ctx):
        def inner(msg):
            return msg == ctx.author
        return inner

    # need to make the check work

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
        print("_____//// Roll bot has loaded sheet_commands ////-----") 

        # C R U D 
    ###################

    # Create - $create_char
    @commands.command()
    async def create_char(self,ctx):
        player = ctx.message.author.name
        printer = Printer()
        classes = Class_info()

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
                    name = await self.client.wait_for('message') # , check=self.check(ctx) 
                    player_sheet["name"] = name.content
                elif i == "look":
                    await ctx.channel.send('Descibe your appearance.')
                    look = await self.client.wait_for('message') # , check=self.check(ctx) 
                    player_sheet['look'] = look.content
                elif i == 'armor' or i == "hitpoints" or i == "damage" or i == "bonds" or i == "inventory":
                    pass
                elif i == "class":
                    await ctx.channel.send(f" choose your character's class from this list: {classes.class_list}")

                    valid_ans = False
                    while valid_ans == False:
                        #### this is how we would implement check that we need to test
                        response = await self.client.wait_for('message') #, check=self.check(ctx)  

                        if response.content in classes.class_list:
                            player_sheet[i] = response.content
                            # print(player_sheet[i])
                            player_sheet['damage'] = self.class_switch(response.content, "damage") #self.class_damage(response.content)
                            player_sheet['bonds'] = self.class_switch(response.content, 'bonds')
                            #self.class_bonds(response.content)
                            valid_ans = True
                        else:
                            await ctx.channel.send(f'choose a valid class {classes.class_list}')
                else:
                    await ctx.channel.send(f"choose a value from this list: {starting_stats} to assign to your {i}")

                    valid_ans = False
                    while valid_ans == False:
                        response = await self.client.wait_for('message') #, check=self.check(ctx)

                        if response.content in starting_stats:
                            starting_stats.pop(starting_stats.index(response.content))
                            player_sheet[i] = response.content
                            valid_ans = True
                        else:
                            await ctx.channel.send(f'choose a valid value {starting_stats}')
            
            player_sheet['hitpoints'] = int(player_sheet['constitution']) + self.class_switch(player_sheet["class"], "hp")

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
                })

            sheet = collection.find_one({"player" : player})

            await printer.sheet_reader(ctx, sheet)
            await printer.bonds_reader(ctx, sheet["bonds"])

    ## Read ##
    
    # $read_sheet - show basic skill sheet 
    @commands.command()
    async def read_sheet(self, ctx):
        player = ctx.author.name
        printer = Printer()

        if collection.find_one({"player": player}):
            sheet = collection.find_one({"player" : player})
            await printer.sheet_reader(ctx, sheet)
        else:
            await ctx.channel.send('You do not have a player sheet, create one by typing "/create-char" into the chat.')

    # $read_bonds - show characters bonds
    @commands.command()
    async def read_bonds(self, ctx):
        player = ctx.author.name
        printer = Printer()

        if collection.find_one({"player": player}):
            sheet = collection.find_one({"player" : player})
            await printer.bonds_reader(ctx, sheet['bonds'])
        else:
            await ctx.channel.send('You do not have a player sheet, create one by typing "/create-char" into the chat.')

    ## Update - $lvl_up  ## this is kind of screwed up now that we've added inventory and bonds 
    # probably best to also not update the sheet on every change 
    # but to send it all up on the end as a single update
    @commands.command()
    async def lvl_up(self, ctx):
        player = ctx.author.name
        query = { "player" : player }
        sheet = collection.find_one(query)
        printer = Printer()

        for key in sheet:
            if key == '_id' or key == "player" or key == "class" or key=="bonds" or key=="damage":
                pass
            else: 
                await ctx.channel.send(f" would you like to update your {key}? y/n")
                answer = await self.client.wait_for('message')
                if answer.content.upper() == 'Y':
                    await ctx.channel.send(f" {key}:{sheet[key]} should equal what?")
                    update_answer = await self.client.wait_for('message') #, check=self.check(ctx)
                    update = {"$set": {key: update_answer.content}}
                    collection.update_one(query, update)
                else:
                    pass

        sheet = collection.find_one({"player" : player})          
        await printer.sheet_reader(ctx, sheet)


    # bonds - $bonds
    @commands.command()
    async def bonds(self, ctx):
        player = ctx.author
        sheet = collection.find_one({"player": player.name})

        bonds = self.class_switch(sheet["class"], "bonds")
        guild = self.client.get_guild(player.guild.id)
        players = []

        for member in guild.members:
    
            if str(member.status) == 'online' and member.bot != True and member.name != player.name:
            # if member.bot != True and member.name != player.name:
                memb_sheet = collection.find_one({"player": member.name})
                memb_name = memb_sheet["name"]
                players.append(memb_name.lower())
                # players.append(member.name)

        for i,b in enumerate(bonds):

            txt = f"selected a player from this list {players} for your bond: \n"
            await ctx.channel.send(txt + b)

            response = await self.client.wait_for('message') # check = self.check(ctx)

            if response.content.lower() in players:
                players.pop(players.index(response.content.lower()))
                bonds[i] = bonds[i].replace('character-name', response.content)

        sheet['bonds'] = bonds
        collection.replace_one({'player': player.name }, sheet, upsert=False)
        printer = Printer()
        await printer.sheet_reader(ctx, sheet)


    ## Delete - $delete_character
    @commands.command()
    async def delete_character(self, ctx):
        player = ctx.message.author
        sheet = collection.find_one({"player": player.name}) # data is just the parsed out bit and deleteing it wont affect the db

        if sheet:
            await ctx.channel.send(f"are you sure you want to delete your character {sheet['name']} - Y / N ")
            answer = await self.client.wait_for('message') #, check=self.check(ctx) 
            if answer.content.upper() == 'Y':
                await ctx.channel.send('your character sheet has been destroyed')
                collection.delete_one({"player": player.name})
                inv_collection.delete_one({"player": player.name})
            else:
                await ctx.channel.send('character not deleted')
                return 

        else:
            await ctx.channel.send('You do not have a player sheet, create one by typing "/create-char" into the chat.')


def setup(client):
    client.add_cog(Sheet_commands(client))

