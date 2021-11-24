import discord
from discord.ext import commands 

import os

class General_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("_____//// Roll bot has loaded general_commands ~.~.~.~.~.") 

    @commands.command()
    async def hey(self, ctx):
        await ctx.send("Hello it is I Roll_bot")

    @commands.command()
    async def here(self, ctx):
        guild_id = ctx.author.guild.id
        guild = self.client.get_guild(guild_id)

        txt= ""
            
        for member in guild.members:
                
            if str(member.status) == 'online' and member.bot != True:
                txt = txt + member.name + ", "

        await ctx.channel.send(txt)

def setup(client):
    client.add_cog(General_commands(client))