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
from discord.ext import tasks
import asyncio
import logging
from discord.ext.commands import CommandNotFound
from discord.ext import commands
import mysql.connector as mariadb
import doracoinsdatabase as dc

#############
global cursor

db=dc.connect()
cursor=db.cursor()
prefix="dd!"
bot = commands.AutoShardedBot(command_prefix=prefix)
bot.remove_command("help")
TOKEN=open("token.txt", "r").read()
print(TOKEN)
cursor.execute("SELECT * FROM doracoins;")
records = cursor.fetchall()
print(str(records))

#############

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

#############

@bot.event
async def on_ready():
    print('----------------------------')
    print('Logged in as')
    print(bot.user)
    print(bot.user.id)
    print('----------------------------')
    print('')
    print('----------------------------')


#############

def givecoins(user, amount):
    global cursor
    # check if user has a doracoins account
    try:
        cursor.execute(
            "SELECT * FROM doracoins WHERE userid = {0}".format(str(user.id))
        )
    except:
        # user doesn't have an account, make one
        cursor.execute(
            "INSERT INTO doracoins (userid, coins) VALUES ({0}, {1});".format(str(user.id),str(amount))
        )
    else:
        # user has account, update coin balance
        cursor.execute(
            "UPDATE doracoins SET coins = {1} WHERE userid = {0};".format(str(user.id),str(amount))
        )

#############

@bot.command(name='yes')
async def yes(ctx):
    givecoins(ctx.author, 50)


bot.run(TOKEN)
