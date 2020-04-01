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

@bot.event
async def on_ready():
    print('----------------------------')
    print('Logged in as')
    print(bot.user)
    print(bot.user.id)
    print('----------------------------')
    print('')
    print('----------------------------')

class CustomCooldown:
    def __init__(self, rate: int, per: float, alter_rate: int, alter_per: float, bucket: discord.ext.commands.BucketType, *, elements):
        self.elements = elements
        self.default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
        self.altered_mapping = commands.CooldownMapping.from_cooldown(alter_rate, alter_per, bucket)

    def __call__(self, ctx: commands.Context):
        skip = False
        for i in self.elements:
            if i[0] == ctx.author.id:
                if int(time.time()) > i[1]:
                    del i
                    break
                else:
                    skip=True
                    bucket = self.altered_mapping.get_bucket(ctx.message)
        if skip == False:
            bucket = self.default_mapping.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error,commands.CommandOnCooldown):
        time = error.retry_after
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        await ctx.send(embed=makeEmbed("Cooooooldown", "Try again in {0:.0f}h, {1:.0f}m, {2:.1f}s.\nThis command has a 1d cooldown.".format(hour, minutes, seconds), colour=16711680))
        return
    if isinstance(error, CommandNotFound) or isinstance(error, commands.MissingPermissions):
        return
    raise error

def givecoins(user, amount):
    global cursor
    # check if user has a doracoins account
    cursor.execute(
        "SELECT userid, coins FROM doracoins"
    )
    exists=False
    coins=0
    for i in cursor.fetchall():
        if str(i[0]) == str(user.id):
            exists=True
            coins=i[1]
            break
    if exists:
        # user has account, update coin balance
        cursor.execute(
            "UPDATE doracoins SET coins = {1} WHERE userid = {0};".format(str(user.id),str(int(coins)+amount))
        )
    else:
        # user doesn't have an account, make one with the coin balance
        cursor.execute(
            "INSERT INTO doracoins (userid, coins) VALUES ({0}, {1});".format(str(user.id),str(amount))
        )

@commands.check(CustomCooldown(1,86400, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='daily')
async def daily(ctx):
    await ctx.channel.send(embed=makeEmbed("Daily", "You've recieved 1,500 coins"))
    givecoins(ctx.author, 1500)

def getcoins(user):
    global cursor
    # check if user has a doracoins account
    cursor.execute(
        "SELECT * FROM doracoins"
    )
    exists=False
    records=cursor.fetchall()
    j=0
    for i in records:
        if str(i[1]) == str(user.id):
            exists=True
            j=i[2]
            break
    if exists:
        return int(j)
    else:
        return 0


bot.run(TOKEN)
