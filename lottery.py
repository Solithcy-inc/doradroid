import discord
from discord import channel
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import random
import os
import asyncio
import sys
import json
import datetime
import requests
import time
import string
import string
from discord.ext import tasks
import asyncio
import logging
from discord.ext.commands import CommandNotFound
from discord.ext import commands
import mysql.connector as mariadb
import doracoinsdatabase as dc
from discord.utils import get

#############
global cursor, whitelist, ranks

db=dc.connect()
cursor=db.cursor()
prefix="dd!"
bot = commands.AutoShardedBot(command_prefix=prefix)
bot.remove_command("help")
TOKEN=open("token.txt", "r").read()

@bot.event
async def on_command_error(ctx, error):
    pass

def makeEmbed(title = "", desc = "", image = None, footer = None, colour = None):
    if colour != None:
        e = discord.Embed(title=title, description=desc, colour=colour, timestamp=datetime.datetime.now())
    else:
        e = discord.Embed(title=title, description=desc, timestamp=datetime.datetime.now())
    if image != None:
        e.set_image(url=image)
    if footer != None:
        e.set_footer(text=footer)
    else:
        if random.randint(1, 15) == random.randint(1, 15):
            e.set_footer(text="")
    return e

bot.event
async def on_ready():
    print('----------------------------')
    print('Logged in as')
    print(bot.user)
    print(bot.user.id)
    print('----------------------------')
    print('Lottery has started')
    print('----------------------------')

async def lottery():
    await bot.wait_until_ready()
    while True:
        asyncio.sleep(172800)
        cursor.execute(
            "SELECT * FROM doracoins"
        )
        amount=random.randint(25000, 100000)
        people=cursor.fetchall()
        while True:
            winner=random.choice(people)
            if bot.get_user(int(winner[1])) in bot.get_guild(412536528561242113).members:
                break
        givecoins(bot.get_user(int(winner[1])), amount)
        await bot.get_channel(693821443493986386).send(embed=makeEmbed("Winner!", "{0} won the lottery! They've won {1} doracoins!".format(bot.get_user(int(winner[1])).mention, str(amount)), colour=1441536))


bot.loop.create_task(lottery())
bot.run(TOKEN)
