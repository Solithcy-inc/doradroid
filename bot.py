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
global cursor, whitelist

whitelist=[330287319749885954]
db=dc.connect()
cursor=db.cursor()
prefix="dd!"
bot = commands.AutoShardedBot(command_prefix=prefix)
bot.remove_command("help")
TOKEN=open("token.txt", "r").read()
print(TOKEN)

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
async def on_command_error(ctx, error):
    if isinstance(error,commands.CommandOnCooldown):
        await ctx.send(embed=makeEmbed("Cooooooldown", "Try again in {0:.2f} seconds.\nThis command has a {1:.1f} second cooldown.".format(error.retry_after, error.cooldown.per), colour=16711680))
        return
    if isinstance(error, CommandNotFound) or isinstance(error, commands.MissingPermissions):
        return
    raise error


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

#############

@has_permissions(administrator=True)
@bot.command(name='admin')
async def admin(ctx):
    await ctx.channel.send("yes")

@commands.check(CustomCooldown(1,2.5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='bal')
async def bal(ctx, user: discord.Member = None):
    if user == None:
        await ctx.channel.send(e=makeEmbed("Balance", str(getcoins(ctx.author))))
    else:
        await ctx.channel.send(e=makeEmbed("{}'s Balance".format(user), str(getcoins(user))))

@bot.command(name='givemoney')
async def givemoney(ctx, amount = None, user: discord.Member = None):
    global whitelist
    if ctx.author.id in whitelist:
        if amount == None:
            await ctx.channel.send(e=makeEmbed("Error", "Please specify an amount of doracoins", colour=16711680))
        elif user == None:
            await ctx.channel.send(e=makeEmbed("Error", "Please specify a member", colour=16711680))
        else:
            givecoins(user, int(amount))
            await ctx.channel.send(e=makeEmbed("Success", "Gave {0} {1} doracoins".format(user, amount), colour=1441536))
    else:
        await ctx.channel.send(e=makeEmbed("Error", "You are not permitted to use this command", colour=16711680))


bot.run(TOKEN)
