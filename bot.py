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
from discord import Webhook, RequestsWebhookAdapter
from deck_of_cards import deck_of_cards as doc
#############
global cursor, whitelist, ranks

with open('ranks.json') as json_file:
    ranks = json.load(json_file)
whitelist=[330287319749885954]
db=dc.connect()
cursor=db.cursor()
prefix="dd!"
bot = commands.AutoShardedBot(command_prefix=prefix)
bot.remove_command("help")
TOKEN=open("token.txt", "r").read()

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
async def on_message(ctx):
    if ctx.author.bot:
        pass
    else:
        if ctx.channel.id==503303471433252887:
            role = get(bot.get_guild(412536528561242113).roles, id=693898081057636352)
            try:
                await ctx.author.remove_roles(role)
            except:
                pass
        if any(ele in ''.join(e for e in ctx.content.lower() if e.isalnum()) for ele in ["nigger", "nigga", "niggar", "nibba", "nibber", "nibbar"]):
            message=ctx
            await ctx.delete()
            try:
                await ctx.author.send("{0}, your message has been deleted and reported to staff.".format(message.author.mention))
            except:
                pass
            await bot.get_channel(412548639798591488 ).send("{0} ({1}) might have said the n-word in {2} in the following message:\n`{3}`".format(message.author, message.author.mention, message.channel.mention, message.content))
        elif any(ele in ''.join(e for e in ctx.content.lower() if e.isalnum()) for ele in ["chingchong", "chingchangchong"]):
            message=ctx
            await ctx.delete()
            try:
                await ctx.author.send("{0}, your message has been deleted and reported to staff.".format(message.author.mention))
            except:
                pass
            await bot.get_channel(412548639798591488 ).send("{0} ({1}) might have said the cc word in {2} in the following message:\n`{3}`".format(message.author, message.author.mention, message.channel.mention, message.content))
        if ctx.content.startswith(prefix):
            await bot.process_commands(ctx)
        else:
            if ctx.channel.id in [574247398855933963, 694220899246932101, 412670226321244161]:
                pass
            else:
                givecoins(ctx.author, random.randint(0,3))

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='dd!help'))
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
            e.set_footer(text="Found a bug? Go to https://github.com/Solithcy-inc/doradroid/issues and report it!")
    return e

def hascustom(user):
    global cursor
    cursor.execute(
        "SELECT hascustom FROM doracoins WHERE userid = {0};".format(str(user.id))
    )
    if cursor.fetchone()[0] == 1:
        return True
    else:
        return False

def givecustom(user):
    global cursor
    cursor.execute(
        "UPDATE doracoins SET hascustom = 1 WHERE userid = {0};".format(str(user.id))
    )

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
        webhook = Webhook.partial(694219649331626075, 'O1LHhL3hwNrFUe2k2HQst_sGIiPbO5J96nu-57Ur8naHe6FAVKey7Xt8owSplSUQcbyJ', adapter=RequestsWebhookAdapter())
        webhook.send(embed=makeEmbed("New user", "{} made an account".format(user)))
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
        await ctx.channel.send(embed=makeEmbed("Balance", str(getcoins(ctx.author))))
    else:
        await ctx.channel.send(embed=makeEmbed("{}'s Balance".format(user.name), str(getcoins(user))))

@commands.check(CustomCooldown(1,2.5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='shop')
async def shop(ctx):
    await ctx.channel.send(embed=makeEmbed("Shop", """Server Memories | 50,000 coins | Let's you send **1** message in Server Memories | `dd!buy servermemories`
Custom Role | 25,000 coins | Gives you a custom role | `dd!buy custom`"""))
    # msg=""
    # for i in ranks:
    #     msg = msg + "**{0}**: {1} doracoins\n".format(i, ranks[i]["cost"])
    # await ctx.channel.send("Shop", "{}".format(msg))

@commands.check(CustomCooldown(1,2.5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='buy')
async def buy(ctx, rank=None, *, namecolour=None):
    if rank == None:
        await ctx.channel.send(embed=makeEmbed("Error", "Please specify a rank to buy", colour=16711680))
    elif rank in ranks:
        if getcoins(ctx.author) >= ranks[rank]['cost']:
            role = get(bot.get_guild(412536528561242113).roles, id=ranks[rank]['id'])
            givecoins(ctx.author, -int(ranks[rank]['cost']))
            await ctx.author.add_roles(role)
            await ctx.channel.send(embed=makeEmbed("Success", "You've bought {}.".format(rank), colour=1441536))
        else:
            await ctx.channel.send(embed=makeEmbed("Error", "You need to have {} coins".format(str(ranks[rank]['cost'])), colour=16711680))
    else:
        if rank=="custom":
            if getcoins(ctx.author) < 25000:
                await ctx.channel.send(embed=makeEmbed("Error", "You need to have 25000 coins", colour=16711680))
            elif namecolour==None:
                if hascustom(ctx.author):
                    await ctx.channel.send(embed=makeEmbed("Error", "You already have a custom role", colour=16711680))
                else:
                    await ctx.channel.send(embed=makeEmbed("Custom Role", "Please run the command again, but with the role name. i.e. `dd!buy custom i am awesome`"))
            else:
                if hascustom(ctx.author):
                    await ctx.channel.send(embed=makeEmbed("Error", "You already have a custom role", colour=16711680))
                else:
                    givecoins(ctx.author, -25000)
                    givecustom(ctx.author)
                    role = await bot.get_guild(412536528561242113).create_role(name=namecolour)
                    await ctx.author.add_roles(role)
                    await ctx.channel.send(embed=makeEmbed("Success", "You've bought a custom role.", colour=1441536))
        else:
            await ctx.channel.send(embed=makeEmbed("Error", "The rank `{}` doesn't exist".format(rank), colour=16711680))

@bot.command(name='givemoney')
async def givemoney(ctx, user: discord.Member = None, amount = None):
    if get(bot.get_guild(412536528561242113).roles, id=416285222452068363) in ctx.author.roles or get(bot.get_guild(412536528561242113).roles, id=412602930601132033) in ctx.author.roles or get(bot.get_guild(412536528561242113).roles, id=412602654741495827) in ctx.author.roles or ctx.author.id == 330287319749885954:
        if user == None:
            await ctx.channel.send(embed=makeEmbed("Error", "Please specify a member", colour=16711680))
        elif amount == None:
            await ctx.channel.send(embed=makeEmbed("Error", "Please specify an amount of doracoins", colour=16711680))
        else:
            givecoins(user, int(amount))
            await ctx.channel.send(embed=makeEmbed("Success", "Gave {0} {1} doracoins".format(user.name, amount), colour=1441536))
    else:
        await ctx.channel.send(embed=makeEmbed("Error", "You are not permitted to use this command", colour=16711680))


@bot.command(name='help')
async def help(ctx):
    await ctx.channel.send(embed = makeEmbed("Help", "Doradroid **[help](https://dorami.xyz/bot/help/)**."))

@bot.command(name='leaderboard', aliases=["lb","top"])
@commands.check(CustomCooldown(1,30, 1, 0, commands.BucketType.user, elements=[]))
async def leaderboard(ctx):
    global cursor
    cursor.execute(
        "SELECT * FROM doracoins ORDER BY coins DESC LIMIT 15"
    )
    records=cursor.fetchall()
    msg=""
    j = 0
    for i in records:
        j += 1
        if j == 1:
            msg=msg+":first_place: {0}: {1} doracoins\n".format(bot.get_user(int(i[1])).name, str(i[2]))
        elif j == 2:
            msg=msg+":second_place: {0}: {1} doracoins\n".format(bot.get_user(int(i[1])).name, str(i[2]))
        elif j == 3:
            msg=msg+":third_place: {0}: {1} doracoins\n".format(bot.get_user(int(i[1])).name, str(i[2]))
        else:
            msg=msg+"{0}) {1}: {2} doracoins\n".format(str(j), bot.get_user(int(i[1])).name, str(i[2]))
    await ctx.channel.send(embed=makeEmbed("Leaderboard", msg, footer="sweats"))

@bot.command(name='gamble', aliases=["bet"])
@commands.check(CustomCooldown(1,30, 1, 0, commands.BucketType.user, elements=[]))
async def gamble(ctx, amount=None):
    if amount == None:
        await ctx.channel.send(embed=makeEmbed("Error", "Please specify an amount of coins", colour=16711680))
    elif int(amount) <= 0:
        await ctx.channel.send(embed=makeEmbed("Error", "Choose a number higher then 0", colour=16711680))
    elif int(amount) > getcoins(ctx.author):
        await ctx.channel.send(embed=makeEmbed("Error", "You don't have {} coins".format(str(amount)), colour=16711680))
    else:
        givecoins(ctx.author, -int(amount))
        message = await ctx.channel.send("Drawing cards")
        deck = doc.DeckOfCards()
        card = deck.give_random_card()
        card2 = deck.give_random_card()
        suits={0:"♠", 1:"♥", 2:"♦", 3:"♣"}
        values={1:"A", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"10", 11:"J", 12:"Q", 13:"K"}
        await asyncio.sleep(1)
        await message.edit(content="{1}'s game\nYou: {0}".format(suits[card.suit]+values[card.value],ctx.author.name))
        await asyncio.sleep(1)
        await message.edit(content="{2}'s game\nYou: {0}\nDoradroid: {1}".format(suits[card.suit]+values[card.value],suits[card2.suit]+values[card2.value],ctx.author.name))
        await asyncio.sleep(1)
        if card.value > card2.value:
            await message.edit(content="{2}'s game\nYou: {0}\nDoradroid: {1}\n**You won twice your bet!**".format(suits[card.suit]+values[card.value],suits[card2.suit]+values[card2.value],ctx.author.name))
            givecoins(ctx.author, int(amount)*2)
        elif card.value < card2.value:
            await message.edit(content="{2}'s game\nYou: {0}\nDoradroid: {1}\n**You lost!**".format(suits[card.suit]+values[card.value],suits[card2.suit]+values[card2.value],ctx.author.name))
        else:
            givecoins(ctx.author, int(amount))
            await message.edit(content="{2}'s game\nYou: {0}\nDoradroid: {1}\n**You drew! Your coins were refunded.**".format(suits[card.suit]+values[card.value],suits[card2.suit]+values[card2.value],ctx.author.name))

@bot.command(name='give', aliases=["share"])
@commands.check(CustomCooldown(1,10, 1, 0, commands.BucketType.user, elements=[]))
async def give(ctx, user: discord.Member = None, amount = None):
    if user == None:
        await ctx.channel.send(embed=makeEmbed("Error", "Please specify a member", colour=16711680))
    elif amount == None:
        await ctx.channel.send(embed=makeEmbed("Error", "Please specify an amount of coins", colour=16711680))
    else:
        if int(amount) <= 0:
            await ctx.channel.send(embed=makeEmbed("Error", "Choose a number higher then 0", colour=16711680))
        elif getcoins(ctx.author) >= int(amount):
            givecoins(ctx.author, -int(amount))
            givecoins(user, int(amount))
            await ctx.channel.send(embed=makeEmbed("Success", "Gave {0} {1} coins".format(user.name, amount), colour=1441536))
        else:
            await ctx.channel.send(embed=makeEmbed("Error", "You don't have {} coins".format(str(amount)), colour=16711680))

bot.run(TOKEN)
