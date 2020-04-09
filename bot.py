import discord
from discord import channel
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import random
import os
import asyncio
import sys
import json
import typing
import datetime
import requests
import time
import time
import string
import praw
import string
from discord.ext import tasks
import asyncio
import logging
from discord.ext.commands import CommandNotFound
from discord.ext import commands
import mysql.connector as mariadb
import doracoinsdatabase as dc
import urllib.parse
from discord.utils import get
from discord import Webhook, RequestsWebhookAdapter
from deck_of_cards import deck_of_cards as doc
import slotmachine as sm

#############

global cursor, whitelist, ranks, reddit, activeitems, petout
activeitems={}
petout={}
reddit = praw.Reddit(client_id='U9RttQtPJc-wOw',client_secret='yQP51k1U2xyKvpCL14ns9pPxXQs',user_agent='DoradroidDiscordBot')
fishprices = {"psychrolutes":3000, "goldfish":100, "carp":20, "cod":20, "haddock":20, "siamese":250, "pike":30, "megamouth":1000, "cyprinodon": 20000, "tuna": 60}
with open('ranks.json') as json_file:
    ranks = json.load(json_file)
whitelist=[330287319749885954]
blacklist=[]
triviaanswers={}
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
    global triviaanswers
    if ctx.author.bot:
        pass
    elif ctx.guild == None:
        pass
    elif str(ctx.author.id) in triviaanswers:
        if ctx.content == triviaanswers[str(ctx.author.id)]["answer"]:
            ctx.channel.send("Correct! You got {0} coins!".format(str(triviaanswers[str(ctx.author.id)]["reward"])))
            givecoins(ctx.author.id, triviaanswers[str(ctx.author.id)]["reward"])
        else:
            ctx.channel.send("Wrong answer!")
        del triviaanswers[str(ctx.author.id)]
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
            if ctx.channel.id in [574247398855933963, 694220899246932101, 412670226321244161, 694532375480107100, 695210918518194196, 695645918111727626]:
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

def place_value(number):
    return ("{:,}".format(number))

def makeEmbed(title = "", desc = "", image = None, footer = None, colour = None, thumbnail = None):
    if colour != None:
        e = discord.Embed(title=title, description=desc, colour=colour, timestamp=datetime.datetime.now())
    else:
        e = discord.Embed(title=title, description=desc, timestamp=datetime.datetime.now())
    if thumbnail != None:
        e.set_thumbnail(url=thumbnail)
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
        # user doesn't have an account, make one with the coin balance
        cursor.execute(
            "INSERT INTO doracoins (userid, coins) VALUES ({0}, {1});".format(str(user.id),str(amount))
        )

def givepet(user, type):
    global cursor
    cursor.execute(
        "SELECT userid FROM pets"
    )
    exists=False
    coins=0
    for i in cursor.fetchall():
        if str(i[0]) == str(user.id):
            exists=True
            break
    health={0:"50"}
    if exists:
        cursor.execute(
            "UPDATE pets SET type = {1} WHERE userid = {0};".format(str(user.id), type)
        )
        cursor.execute(
            "UPDATE pets SET health = {1} WHERE userid = {0};".format(str(user.id), health[type])
        )
    else:
        cursor.execute(
            "INSERT INTO pets (userid, type, health) VALUES ({0}, {1}, {2});".format(str(user.id),str(type), health[type])
        )

def giveitem(user, item, amount=1):
    global cursor
    # check if user has a doracoins account
    cursor.execute(
        "SELECT userid, {} FROM inventory".format(item)
    )
    exists=False
    coins=0
    for i in cursor.fetchall():
        if str(i[0]) == str(user.id):
            exists=True
            itemamount=i[1]
            break
    if exists:
        # user has account, update inventory
        cursor.execute(
            "UPDATE inventory SET {2} = {1} WHERE userid = {0};".format(str(user.id),str(int(itemamount)+amount), item)
        )
    else:
        # user doesn't have an account, make one with the inventory
        cursor.execute(
            "INSERT INTO inventory (userid, {2}) VALUES ({0}, {1});".format(str(user.id),str(amount), item)
        )

def getinv(user):
    global cursor
    # check if user has a doracoins account
    cursor.execute(
        "SELECT * FROM inventory WHERE userid={}".format(str(user.id))
    )
    records=cursor.fetchall()
    if records!=[]:
        j = 0
        empty=True
        dict1 = {}
        dict2 = {0:"", 1:"", 2:"carp", 3:"cod", 4:"bait", 5:"goldfish", 6:"haddock", 7:"megamouth", 8:"pike", 9:"psychrolutes", 10:"siamese", 11:"cyprinodon", 12:"tuna", 13:"fishlim", 14:"job", 15:"dorafish", 16:"clover", 17:"autofish"}
        for i in records[0]:
            if j in [0,1]:
                pass
            else:
                if i != 0:
                    empty=False
                dict1[dict2[j]]=i
            j+=1
        if empty:
            giveitem(user, "fishlim", 1)
            return getinv(user)
        else:
            return dict1
    else:
        giveitem(user, "rod", 1)
        return getinv(user)

def getpet(user):
    global cursor
    # check if user has a pet account
    cursor.execute(
        "SELECT * FROM pets WHERE userid={}".format(str(user.id))
    )
    records=cursor.fetchall()
    if records!=[]:
        j = 0
        empty=True
        dict1 = {}
        dict2 = {0:"", 1:"", 2:"type", 3:"love", 4:"attack", 5:"health", 6:"defence"}
        for i in records[0]:
            if j in [0,1]:
                pass
            else:
                dict1[dict2[j]]=i
            j+=1
        return dict1
    else:
        return None

def updatepet(user, var, amount):
    global cursor
    if getpet(user) != None:
        cursor.execute(
            "UPDATE pets SET {0} = {1} WHERE userid = {2};".format(var, amount, str(user.id))
        )
        return 200
    else:
        return None

def checkslots(slot):
    j=""
    amount=1
    winner=""
    for i in slot:
        if j == i:
            amount+=1
            winner=i
        else:
            j = i
    if winner == "<:bar:694563172664999966>":
        if amount == 2:
            return 2
        else:
            return 7
    elif winner == "<:777:694563174141394965>":
        if amount == 2:
            return 1.5
        else:
            return 5
    elif winner == "<:cherry:694563964234760264>":
        if amount == 2:
            return 1.3
        else:
            return 4
    elif winner == "<:grapes:694563172333650111>":
        if amount == 2:
            return 1.2
        else:
            return 3.5
    elif winner == "<:orange:694563172333519010>":
        if amount == 2:
            return 1.1
        else:
            return 3
    elif winner == "<:bannana:694563172778246174>":
        if amount == 2:
            return 1.1
        else:
            return 2
    elif winner == "<:melon:694563172689903616>":
        if amount == 2:
            return 1
        else:
            return 2
    elif winner in ["<:apple:694563207888633936>", "<:lime:694563173025448017>"]:
        if amount == 2:
            return 1
        else:
            return 1.5
    else:
        return 0

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

async def fish(ctx):
    lucky=False
    if str(ctx.author.id) in activeitems:
        if "clover" in activeitems[str(ctx.author.id)]:
            lucky=True
        else:
            lucky=False
    else:
        lucky=False
    if lucky==False:
        chance=random.randint(1, 100000)
        if chance <= 10:
            print("Cyprinodon Diabolis captured")
            giveitem(ctx.author, "cyprinodon", 1)
            return "cyprinodon"
        else:
            chance=random.randint(1, 100000)
            if chance <= 100:
                print("Psychrolutes Marcidus captured")
                giveitem(ctx.author, "psychrolutes", 1)
                return "psychrolutes"
            else:
                chance=random.randint(1, 100000)
                if chance <= 1000:
                    giveitem(ctx.author, "megamouth", 1)
                    return "megamouth"
                else:
                    chance=random.randint(1, 100000)
                    if chance <= 3500:
                        giveitem(ctx.author, "siamese", 1)
                        return "siamese"
                    else:
                        chance=random.randint(1, 100000)
                        if chance <= 12500:
                            giveitem(ctx.author, "goldfish", 1)
                            return "goldfish"
                        else:
                            chance=random.randint(1, 100000)
                            if chance <= 20000:
                                giveitem(ctx.author, "tuna", 1)
                                return "tuna"
                            else:
                                chance=random.randint(1, 100000)
                                if chance <= 35000:
                                    giveitem(ctx.author, "pike", 1)
                                    return "pike"
                                else:
                                    chance=random.randint(1, 100000)
                                    if chance <= 70000:
                                        types=['cod','carp','haddock']
                                        thetype=random.choice(types)
                                        giveitem(ctx.author, thetype, 1)
                                        return thetype
                                    else:
                                        return None
    else:
        chance=random.randint(1, 100000)
        if chance <= 20:
            print("Cyprinodon Diabolis captured")
            giveitem(ctx.author, "cyprinodon", 1)
            return "cyprinodon"
        else:
            chance=random.randint(1, 100000)
            if chance <= 200:
                print("Psychrolutes Marcidus captured")
                giveitem(ctx.author, "psychrolutes", 1)
                return "psychrolutes"
            else:
                chance=random.randint(1, 100000)
                if chance <= 2000:
                    giveitem(ctx.author, "megamouth", 1)
                    return "megamouth"
                else:
                    chance=random.randint(1, 100000)
                    if chance <= 6000:
                        giveitem(ctx.author, "siamese", 1)
                        return "siamese"
                    else:
                        chance=random.randint(1, 100000)
                        if chance <= 20000:
                            giveitem(ctx.author, "goldfish", 1)
                            return "goldfish"
                        else:
                            chance=random.randint(1, 100000)
                            if chance <= 30000:
                                giveitem(ctx.author, "tuna", 1)
                                return "tuna"
                            else:
                                chance=random.randint(1, 100000)
                                if chance <= 45000:
                                    giveitem(ctx.author, "pike", 1)
                                    return "pike"
                                else:
                                    chance=random.randint(1, 100000)
                                    if chance <= 100000:
                                        types=['cod','carp','haddock']
                                        thetype=random.choice(types)
                                        giveitem(ctx.author, thetype, 1)
                                        return thetype
                                    else:
                                        return None


#############

@commands.check(CustomCooldown(1,30, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='secret')
async def secret(ctx):
    await ctx.channel.send("I'm not here.")

@commands.check(CustomCooldown(1,7.5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='use')
async def meme(ctx, *, item=None):
    global activeitems
    if item == None:
        await ctx.channel.send(embed=makeEmbed("Error", "Please specify something to use", footer="Jesus Christ isn't that self explanatory", colour=16711680))
    elif item == "rod":
        await ctx.channel.send("`dd!fish` exists holy heck bro")
    elif item == "clover":
        try:
            clovers = getinv(ctx.author)['clover']
        except:
            clovers = 0
        if clovers>0:
            contin=False
            if str(ctx.author.id) in activeitems:
                if "clover" in activeitems[str(ctx.author.id)]:
                    await ctx.channel.send("You already have a clover active")
                else:
                    activeitems[str(ctx.author.id)]["clover"]=time.time()+60*10
                    contin=True
            else:
                activeitems[str(ctx.author.id)]={"clover":time.time()+60*10}
                contin=True
            if contin:
                await ctx.channel.send("Because of your 4 leafed clover, you now have a luck boost for the next 10 minutes! This applies to fishing and betting.")
                giveitem(ctx.author, "clover", -1)
                await asyncio.sleep(60*10)
                try:
                    await ctx.author.send("Your clover has stopped giving you luck.")
                except:
                    pass
                activeitems[str(ctx.author.id)].pop("clover", None)
        else:
            await ctx.channel.send("You don't even have a clover bro")
    elif item == "autofish":
        try:
            autofishers = getinv(ctx.author)['autofish']
        except:
            autofishers = 0
        if autofishers>0:
            contin=False
            if str(ctx.author.id) in activeitems:
                if "autofish" in activeitems[str(ctx.author.id)]:
                    await ctx.channel.send("You already have an auto fisher active")
                else:
                    activeitems[str(ctx.author.id)]["autofish"]=time.time()+60*10
                    contin=True
            else:
                activeitems[str(ctx.author.id)]={"autofish":time.time()+60*10}
                contin=True
            if contin:
                await ctx.channel.send("Your auto fisher will fish once every 15 seconds for the next 10 minutes (being affected by luck and without using bait), and ping you when it's finished.")
                giveitem(ctx.author, "autofish", -1)
                await asyncio.sleep(600)
                hascaught=[]
                for i in range(0,40):
                    hascaught.append(await fish(ctx))
                amountoffish={"tuna": 0, "psychrolutes":0, "goldfish":0, "carp":0, "cod":0, "haddock":0, "siamese":0, "pike":0, "megamouth":0, "cyprinodon": 0}
                for i in hascaught:
                    if i != None:
                        amountoffish[i]+=1
                msg=""
                fishtypes={"psychrolutes":"Psychrolutes Marcidus :O rare", "goldfish":"Goldfish", "tuna":"Tuna", "carp":"Carp", "cod":"Cod", "haddock":"Haddock", "siamese":"Siamese Fighting Fish", "pike":"Northern Pike", "megamouth":"Megamouth Shark", "cyprinodon": "Cyprinodon Diabolis :OOOO"}
                amountoffishkeys=sorted(amountoffish, key=str.lower)
                for i in amountoffishkeys:
                    if amountoffish[i] == 0:
                        pass
                    else:
                        msg=msg+"**{0}**: {1}\n".format(fishtypes[i], str(amountoffish[i]))
                await ctx.channel.send("{1}\nI have caught these fish, and they are now in your inventory:\n>>> {0}".format(msg,ctx.author.mention))
                activeitems[str(ctx.author.id)].pop("autofish", None)
        else:
            await ctx.channel.send("You don't even have an auto fisher bro")
    else:
        await ctx.channel.send(embed=makeEmbed("Error", "`{}` doesn't exist.".format(item), colour=16711680))

@commands.check(CustomCooldown(1,5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='active')
async def active(ctx, user: discord.Member = None):
    items=None
    if user==None:
        id=str(ctx.author.id)
    else:
        id=str(user.id)
    if id in activeitems:
        items=activeitems[id]
    if items == None or items == {}:
        if user==None:
            await ctx.channel.send("You have no active things")
        else:
            await ctx.channel.send("{} has no active things".format(user.name))
    else:
        msg=""
        for i in items:
            if i == "clover":
                m, s = divmod(activeitems[id]["clover"]-time.time(), 60)
                h, m = divmod(m, 60)
                msg=msg+"**Clover luck boost**: {0:.0f}m {1:.0f}s\n".format(m, s)
            elif i == "autofish":
                m, s = divmod(activeitems[id]["autofish"]-time.time(), 60)
                h, m = divmod(m, 60)
                msg=msg+"**Auto Fisher**: {0:.0f}m {1:.0f}s\n".format(m, s)
            elif i == "search":
                m, s = divmod(activeitems[id]["search"]-time.time(), 60)
                h, m = divmod(m, 60)
                petinfo=getpet(ctx.author)
                types={0:"ball"}
                msg=msg+"**Pet {2} searching**: {0:.0f}m {1:.0f}s\n".format(m, s, types[petinfo["type"]])
            elif i == "attackprep":
                m, s = divmod(activeitems[id]["attackprep"]-time.time(), 60)
                h, m = divmod(m, 60)
                petinfo=getpet(ctx.author)
                types={0:"ball"}
                msg=msg+"**Pet {2} preparing for attack**: {0:.0f}m {1:.0f}s\n".format(m, s, types[petinfo["type"]])
            elif i == "attackmove":
                m, s = divmod(activeitems[id]["attackmove"]-time.time(), 60)
                h, m = divmod(m, 60)
                petinfo=getpet(ctx.author)
                types={0:"ball"}
                msg=msg+"**Pet {2} going to target's house**: {0:.0f}m {1:.0f}s\n".format(m, s, types[petinfo["type"]])
            elif i == "attackfin":
                m, s = divmod(activeitems[id]["attackfin"]-time.time(), 60)
                h, m = divmod(m, 60)
                petinfo=getpet(ctx.author)
                types={0:"ball"}
                msg=msg+"**Pet {2} coming back home**: {0:.0f}m {1:.0f}s\n".format(m, s, types[petinfo["type"]])
            elif i == "defend":
                m, s = divmod(activeitems[id]["defend"]-time.time(), 60)
                h, m = divmod(m, 60)
                petinfo=getpet(ctx.author)
                types={0:"ball"}
                msg=msg+"**Pet {2} defending**: {0:.0f}m {1:.0f}s\n".format(m, s, types[petinfo["type"]])
            else:
                msg=msg+"Unknown item\n"
        if user==None:
            await ctx.channel.send("**__Your active things__**:\n>>> {}".format(msg))
        else:
            await ctx.channel.send("**__{1}'s active things__**:\n>>> {0}".format(msg, user.name))


@commands.check(CustomCooldown(1,5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='meme')
async def meme(ctx):
    while True:
        sub = reddit.subreddit(random.choice(['memes', 'dankmemes'])).random()
        if sub.domain in ["i.redd.it", "i.imgur.com"] and not sub.over_18:
            break
    await ctx.channel.send(embed=makeEmbed("{}".format(sub.title), "Score: {0}\n[Image link]({1})".format(place_value(sub.score), sub.url), image=sub.url))

@bot.command(name='pet')
async def pet(ctx, arg=None, arg2:typing.Union[discord.Member, str]=None):
    global petout, cursor
    types={0:"ball"}
    if arg==None:
        if getpet(ctx.author) == None:
            await ctx.channel.send("You can run the following command:\n>>> `dd!pet get`")
        else:
            await ctx.channel.send("""You can run the following commands:
>>> `dd!pet get`
`dd!pet info`

`dd!pet play` (increases love points)
`dd!pet train` (increases attack points)
`dd!pet karate` (increases defence points)

`dd!pet search` (costs 3 love points)
`dd!pet attack [user]` (costs 7 attack points)
`dd!pet defend` (costs 6 defence points)
""")
    elif arg=="info":
        petinfo=getpet(ctx.author)
        if petinfo==None:
            await ctx.channel.send("You don't have a pet.")
        else:
            await ctx.channel.send(embed=makeEmbed("Your pet {}".format(types[petinfo["type"]]), "**Love**: {0}/10\n**Attack**: {1}/10\n**Defence**: {2}/10\n**Health**: {3}".format(petinfo["love"], petinfo["attack"], petinfo["defence"], petinfo["health"]), thumbnail="https://www.kindpng.com/picc/b/538-5386211_smiley-ball-png.png"))
    elif str(ctx.author.id) in activeitems and "search" in activeitems[str(ctx.author.id)]:
        petinfo=getpet(ctx.author)
        await ctx.channel.send("Your pet {0} is currently out searching.".format(types[petinfo["type"]]))
    elif str(ctx.author.id) in activeitems and "attackprep" in activeitems[str(ctx.author.id)]:
        petinfo=getpet(ctx.author)
        await ctx.channel.send("Your pet {0} is currently preparing for attack.".format(types[petinfo["type"]]))
    elif str(ctx.author.id) in activeitems and "attackmove" in activeitems[str(ctx.author.id)]:
        petinfo=getpet(ctx.author)
        await ctx.channel.send("Your pet {0} is currently going to their victim's house.".format(types[petinfo["type"]]))
    elif str(ctx.author.id) in activeitems and "attackfin" in activeitems[str(ctx.author.id)]:
            petinfo=getpet(ctx.author)
            await ctx.channel.send("Your pet {0} is currently on their way home.".format(types[petinfo["type"]]))
    elif str(ctx.author.id) in activeitems and "defend" in activeitems[str(ctx.author.id)]:
            petinfo=getpet(ctx.author)
            await ctx.channel.send("Your pet {0} is currently defending you.".format(types[petinfo["type"]]))
    elif arg=="get":
        if arg2==None:
            await ctx.channel.send("You can get the following pets:\n>>> `dd!pet get ball` (500 coins)")
        elif arg2=="ball":
            if getcoins(ctx.author)>=500:
                petinfo=getpet(ctx.author)
                cursor.execute("DELETE FROM pets WHERE userid = {};".format(ctx.author.id))
                givecoins(ctx.author, -500)
                givepet(ctx.author, 0)
                petout[str(ctx.author.id)]={}
                if petinfo == None:
                    await ctx.channel.send("You now have a pet ball. You can run more commands now, check them out by running `dd!pet`.")
                else:
                    await ctx.channel.send("You abandoned your pet {} for a new pet ball.".format(types[petinfo["type"]]))
            else:
                await ctx.channel.send("A pet ball costs 500.")
        else:
            await ctx.channel.send("The pet {} doesn't exist.".format(arg2))
    elif arg=="play":
        if str(ctx.author.id) in petout:
            if "love" in petout[str(ctx.author.id)]:
                cooldown=petout[str(ctx.author.id)]["love"]
            else:
                cooldown=0
        else:
            petout[str(ctx.author.id)]={}
            cooldown=0
        if cooldown>time.time():
            m, s = divmod(cooldown-time.time(), 60)
            h, m = divmod(m, 60)
            await ctx.channel.send("Your pet doesn't want to play. Try again in {0:.0f}m {1:.0f}s.".format(m, s))
        else:
            petinfo=getpet(ctx.author)
            if petinfo==None:
                await ctx.channel.send("You don't have a pet.")
            else:
                petout[str(ctx.author.id)]["love"]=time.time()+600
                places=["in the skatepark","in the bowling alley","behind the theatre","in the cinema","in the church","on Discord","FoRkNiTe","on Doradroid ||lucky you||","hide and seek","on the computer but ended up hacking NASA accidentally","on GitHub ||somehow||","Spotify and danced to Bitch Lasagna","in prison","with Soli","with Jaer","in the hospital","with COVID-19"]
                loveval=random.randint(1,2)
                updatepet(ctx.author, "love", petinfo["love"]+loveval)
                if petinfo["love"]+loveval>10:
                    updatepet(ctx.author, "love", 10)
                    await ctx.channel.send("You and your pet {0} played {1}. Your pet's **love** points are maxed out.".format(types[petinfo["type"]], random.choice(places)))
                else:
                    await ctx.channel.send("You and your pet {0} played {1}. Your pet's **love** points went up by {2}.".format(types[petinfo["type"]], random.choice(places), loveval))
    elif arg=="train":
        if str(ctx.author.id) in petout:
            if "attack" in petout[str(ctx.author.id)]:
                cooldown=petout[str(ctx.author.id)]["attack"]
            else:
                cooldown=0
        else:
            petout[str(ctx.author.id)]={}
            cooldown=0
        if cooldown>time.time():
            m, s = divmod(cooldown-time.time(), 60)
            h, m = divmod(m, 60)
            await ctx.channel.send("Your pet is too tired to train. Try again in {0:.0f}m {1:.0f}s.".format(m, s))
        else:
            petinfo=getpet(ctx.author)
            if petinfo==None:
                await ctx.channel.send("You don't have a pet.")
            else:
                petout[str(ctx.author.id)]["attack"]=time.time()+600
                attackval=random.randint(1,3)
                updatepet(ctx.author, "attack", petinfo["attack"]+attackval)
                if petinfo["attack"]+attackval>10:
                    updatepet(ctx.author, "attack", 10)
                    await ctx.channel.send("You and your pet {0} trained in the gym. Your pet's **attack** points are maxed out.".format(types[petinfo["type"]]))
                else:
                    await ctx.channel.send("You and your pet {0} trained in the gym. Your pet's **attack** points went up by {1}.".format(types[petinfo["type"]], attackval))
    elif arg=="karate":
        if str(ctx.author.id) in petout:
            if "defence" in petout[str(ctx.author.id)]:
                cooldown=petout[str(ctx.author.id)]["defence"]
            else:
                cooldown=0
        else:
            petout[str(ctx.author.id)]={}
            cooldown=0
        if cooldown>time.time():
            m, s = divmod(cooldown-time.time(), 60)
            h, m = divmod(m, 60)
            await ctx.channel.send("Your pet is too tired to do karate. Try again in {0:.0f}m {1:.0f}s.".format(m, s))
        else:
            petinfo=getpet(ctx.author)
            if petinfo==None:
                await ctx.channel.send("You don't have a pet.")
            else:
                petout[str(ctx.author.id)]["defence"]=time.time()+600
                attackval=random.randint(1,3)
                updatepet(ctx.author, "defence", petinfo["defence"]+attackval)
                if petinfo["defence"]+attackval>10:
                    updatepet(ctx.author, "attack", 10)
                    await ctx.channel.send("You and your pet {0} did karate. Your pet's **defence** points are maxed out.".format(types[petinfo["type"]]))
                else:
                    await ctx.channel.send("You and your pet {0} did karate. Your pet's **defence** points went up by {1}.".format(types[petinfo["type"]], attackval))
    elif arg=="search":
        petinfo=getpet(ctx.author)
        if petinfo==None:
            await ctx.channel.send("You don't have a pet.")
        else:
            if petinfo["love"]>=4:
                updatepet(ctx.author, "love", petinfo["love"]-4)
                await ctx.channel.send("Your pet {0} has gone searching for coins and items. It will be back in 5 minutes.".format(types[petinfo["type"]]))
                if str(ctx.author.id) in activeitems:
                    if "search" in activeitems[str(ctx.author.id)]:
                        await ctx.channel.send("Your pet is already out searching.")
                    else:
                        activeitems[str(ctx.author.id)]["search"]=time.time()+60*5
                else:
                    activeitems[str(ctx.author.id)]={"search":time.time()+60*5}
                await asyncio.sleep(60*5)
                if "search" in activeitems[str(ctx.author.id)]:
                    activeitems[str(ctx.author.id)].pop("search", None)
                    coins=0
                    items=[]
                    for i in range(0,20):
                        if random.randint(0,10)<=7:
                            coins+=random.randint(1,100)
                        elif random.randint(0,15)<=5:
                            items.append(random.choice(['autofish','clover','haddock','carp','cod','haddock','carp','cod','','','','']))
                    amounts={'autofish':0,'clover':0,'haddock':0,'carp':0,'cod':0,'':0}
                    for i in items:
                        amounts[i]+=1
                    msg="**Coins**: {}\n".format(coins)
                    givecoins(ctx.author, coins)
                    for i in amounts:
                        if i == '':
                            pass
                        else:
                            if amounts[i] > 0:
                                giveitem(ctx.author, i, amounts[i])
                                if i == 'autofish':
                                    msg=msg+"**Autofisher**: {}\n".format(amounts[i])
                                elif i == 'clover':
                                    msg=msg+"**4 Leaved Clover**: {}\n".format(amounts[i])
                                elif i == 'haddock':
                                    msg=msg+"**Haddock**: {}\n".format(amounts[i])
                                elif i == 'carp':
                                    msg=msg+"**Carp**: {}\n".format(amounts[i])
                                elif i == 'cod':
                                    msg=msg+"**Cod**: {}\n".format(amounts[i])
                    await ctx.channel.send("{0}, your pet {1} has finished searching and has got the following:\n>>> {2}".format(ctx.author.mention, types[petinfo["type"]], msg))
            else:
                if random.randint(0,10)<4:
                    cursor.execute("DELETE FROM pets WHERE userid = {};".format(ctx.author.id))
                    petout[str(ctx.author.id)]={}
                    await ctx.channel.send("Your pet {} got bored of being used for coins and items, so it left you.".format(types[petinfo["type"]]))
                else:
                    await ctx.channel.send("Your pet {} doesn't love you enough.".format(types[petinfo["type"]]))
    elif arg=="attack":
        petinfo=getpet(ctx.author)
        if petinfo==None:
            await ctx.channel.send("You don't have a pet.")
        else:
            if type(arg2) is str or arg2==None:
                await ctx.channel.send("Please mention a user")
            else:
                if petinfo["attack"]>=7:
                    updatepet(ctx.author, "attack", petinfo["attack"]-7)
                    await ctx.channel.send("Your pet {0} is getting ready for attack! It will be back in 5 minutes.".format(types[petinfo["type"]]))
                    if str(ctx.author.id) in activeitems:
                        if "attackprep" in activeitems[str(ctx.author.id)]:
                            await ctx.channel.send("Your pet is already getting ready.")
                        else:
                            activeitems[str(ctx.author.id)]["attackprep"]=time.time()+60*5
                    else:
                        activeitems[str(ctx.author.id)]={"attackprep":time.time()+60*5}
                    await asyncio.sleep(60*5)
                    activeitems[str(ctx.author.id)].pop("attackprep", None)
                    await ctx.channel.send("{0}, your pet {1} has finished getting ready, and is now on their way to attack {2}! It'll be there in 30 seconds.".format(ctx.author.mention, types[petinfo["type"]], arg2.name))
                    if str(ctx.author.id) in activeitems:
                        if "attackmove" in activeitems[str(ctx.author.id)]:
                            await ctx.channel.send("Your pet is already on their way.")
                        else:
                            activeitems[str(ctx.author.id)]["attackmove"]=time.time()+30
                    else:
                        activeitems[str(ctx.author.id)]={"attackmove":time.time()+30}
                    await asyncio.sleep(30)
                    activeitems[str(ctx.author.id)].pop("attackmove", None)
                    if str(arg2.id) in activeitems and "defend" in activeitems[str(arg2.id)]:
                        victimpetinfo=getpet(arg2)
                        msg="{0}, your pet {1} turned up at {2}'s house, but his pet {3} was defending him! They started fighting:\n".format(ctx.author.mention, types[petinfo["type"]], arg2.mention, types[victimpetinfo["type"]])
                        themessage=await ctx.channel.send(msg)
                        victimhealth=victimpetinfo["health"]
                        userhealth=petinfo["health"]
                        await asyncio.sleep(1)
                        msg=msg+"> **{0}'s pet's health: {1}**\n".format(ctx.author.name, userhealth)
                        msg=msg+"> **{0}'s pet's health: {1}**\n".format(arg2.name, victimhealth)
                        await themessage.edit(content=msg)
                        while True:
                            await asyncio.sleep(1)
                            if userhealth>0:
                                damage=random.randint(-3,10)
                                if damage <= 0:
                                    msg=msg+"> **{0}'s pet** missed. Remaining health: **{1}**\n".format(ctx.author.name, victimhealth)
                                else:
                                    victimhealth+=-damage
                                    msg=msg+"> **{0}'s pet** dealt **{1}** damage to {2}'s pet. Remaining health: **{3}**\n".format(ctx.author.name, damage, arg2.name, victimhealth)
                            else:
                                break
                            await themessage.edit(content=msg)
                            await asyncio.sleep(1)
                            if victimhealth>0:
                                damage=random.randint(-3,10)
                                if damage <= 0:
                                    msg=msg+"> **{0}'s pet** missed. Remaining health: **{1}**\n".format(arg2.name, userhealth)
                                else:
                                    userhealth+=-damage
                                    msg=msg+"> **{2}'s pet** dealt {1} damage to {0}'s pet. Remaining health: **{3}**\n".format(ctx.author.name, damage, arg2.name, userhealth)
                            else:
                                break
                            await themessage.edit(content=msg)
                        if userhealth<=0:
                            msg=msg+"> \n> __**{0}'s pet died.**__\n".format(ctx.author.name)
                            cursor.execute("DELETE FROM pets WHERE userid = {};".format(ctx.author.id))
                            petout[str(ctx.author.id)]={}
                            await themessage.edit(content=msg)
                            msg=msg+"> \n> __**{0}'s pet won!**__\n{1} wasn't attacked.".format(arg2.name, arg2.mention)
                            await asyncio.sleep(1)
                            await themessage.edit(content=msg)
                        else:
                            msg=msg+"> \n> __**{0}'s pet died.**__\n".format(arg2.name)
                            cursor.execute("DELETE FROM pets WHERE userid = {};".format(arg2.id))
                            petout[str(arg2.id)]={}
                            await themessage.edit(content=msg)
                            msg=msg+"> \n> __**{0}'s pet won!**__\n".format(ctx.author.name)
                            await asyncio.sleep(1)
                            await themessage.edit(content=msg)
                            amount = random.randint(2,2500)
                            if amount > getcoins(arg2):
                                amount = getcoins(arg2)
                            givecoins(arg2, -amount)
                            await asyncio.sleep(1)
                            msg=msg+"\n{0}'s pet {1} violently attacked {2}, and stole {3} coins. Your pet is coming back home, it'll be back in 30 seconds.".format(ctx.author.mention, types[petinfo["type"]], arg2.mention, amount)
                            if str(ctx.author.id) in activeitems:
                                if "attackfin" in activeitems[str(ctx.author.id)]:
                                    await ctx.channel.send("Your pet is already coming home.")
                                else:
                                    activeitems[str(ctx.author.id)]["attackfin"]=time.time()+30
                            else:
                                activeitems[str(ctx.author.id)]={"attackfin":time.time()+30}
                            await themessage.edit(content=msg)
                            await asyncio.sleep(30)
                            if "attackfin" in activeitems[str(ctx.author.id)]:
                                activeitems[str(ctx.author.id)].pop("attackfin", None)
                                givecoins(ctx.author, amount)
                                await ctx.channel.send("{0}, your pet {1} has returned home, and given you the {2} coins it's stolen.".format(ctx.author.mention, types[petinfo["type"]], amount))
                    else:
                        amount = random.randint(2,2500)
                        if amount > getcoins(arg2):
                            amount = getcoins(arg2)
                        givecoins(arg2, -amount)
                        await ctx.channel.send("{0}, your pet {1} is at {2}'s house, has violently attacked them, and stole {3} coins. Your pet is coming back home, it'll be back in 30 seconds.".format(ctx.author.mention, types[petinfo["type"]], arg2.mention, amount))
                        if str(ctx.author.id) in activeitems:
                            if "attackfin" in activeitems[str(ctx.author.id)]:
                                await ctx.channel.send("Your pet is already coming home.")
                            else:
                                activeitems[str(ctx.author.id)]["attackfin"]=time.time()+30
                        else:
                            activeitems[str(ctx.author.id)]={"attackfin":time.time()+30}
                        await asyncio.sleep(30)
                        if "attackfin" in activeitems[str(ctx.author.id)]:
                            activeitems[str(ctx.author.id)].pop("attackfin", None)
                            givecoins(ctx.author, amount)
                            await ctx.channel.send("{0}, your pet {1} has returned home, and given you the {2} coins it's stolen.".format(ctx.author.mention, types[petinfo["type"]], amount))
                else:
                    await ctx.channel.send("Your pet {} isn't strong enough.".format(types[petinfo["type"]]))
    elif arg=="defend":
        petinfo=getpet(ctx.author)
        if petinfo==None:
            await ctx.channel.send("You don't have a pet.")
        else:
            if petinfo["defence"]>=6:
                updatepet(ctx.author, "defence", petinfo["defence"]-6)
                await ctx.channel.send("Your pet {0} will now defend you from attack for the next 8 minutes!".format(types[petinfo["type"]]))
                if str(ctx.author.id) in activeitems:
                    if "attackprep" in activeitems[str(ctx.author.id)]:
                        await ctx.channel.send("Your pet is already defending you.")
                    else:
                        activeitems[str(ctx.author.id)]["defend"]=time.time()+60*8
                else:
                    activeitems[str(ctx.author.id)]={"defend":time.time()+60*8}
                await asyncio.sleep(60*8)
                if "defend" in activeitems[str(ctx.author.id)]:
                    activeitems[str(ctx.author.id)].pop("defend", None)
                    await ctx.channel.send("{0}, your pet {1} has stopped defending you!".format(ctx.author.mention, types[petinfo["type"]]))
            else:
                await ctx.channel.send("Your pet {0} is not strong enough in the way of defence.".format(types[petinfo["type"]]))



@has_permissions(administrator=True)
@bot.command(name='admin')
async def admin(ctx):
    await ctx.channel.send("yes")

@bot.command(name='restart')
async def restart(ctx):
    if ctx.author.id!=330287319749885954:
        await ctx.channel.send("no fuck you man")
    else:
        await ctx.channel.send("----------------------------\n\n         **__RESTARTING__**\n\n----------------------------")
        print("----------------------------")
        print("")
        print("RESTARTING")
        print("")
        print("----------------------------")
        os.execl(sys.executable, sys.executable, *sys.argv)

@bot.command(name='exit')
async def exit(ctx):
    if ctx.author.id!=330287319749885954:
        await ctx.channel.send("no fuck you man")
    else:
        await ctx.channel.send("----------------------------\n\n           **__STOPPING__**\n\n----------------------------")
        os._exit(0)

@commands.check(CustomCooldown(1,30, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='announce')
async def announce(ctx, *, msg=None):
    if ctx.author.id in [330287319749885954]:
        if msg == None:
            await ctx.channel.send("You didn't specify a message to send.")
        else:
            global cursor
            cursor.execute(
                "SELECT * FROM doracoins WHERE dms=1"
            )
            records=cursor.fetchall()
            howmany=len(records)
            confirmmsg=await ctx.channel.send("Sending the following message to {0} people:\n{1}".format(howmany, msg))
            success=0
            for i in records:
                try:
                    await bot.get_user(int(i[1])).send("**__Announcement from {0}:__**\n\n{1}".format(ctx.author.name, msg))
                    success+=1
                except:
                    pass
            await confirmmsg.edit(content="Successfully sent the message to {0} out of {1} people.".format(success, howmany))
    else:
        await ctx.channel.send("No.")

@commands.check(CustomCooldown(1,30, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='dms')
async def dms(ctx):
        global cursor
        # check if user has a doracoins account
        cursor.execute(
            "SELECT userid FROM doracoins WHERE dms=1"
        )
        exists=False
        coins=0
        for i in cursor.fetchall():
            if str(i[0]) == str(ctx.author.id):
                exists=True
                break
        if exists:
            cursor.execute(
                "UPDATE doracoins SET dms = 0 WHERE userid = {0};".format(str(ctx.author.id))
            )
            await ctx.channel.send("Successfully unsubscribed from DM announcements. Run the command again to sign up.")
        else:
            givecoins(ctx.author, 0)
            cursor.execute(
                "UPDATE doracoins SET dms = 1 WHERE userid = {0};".format(str(ctx.author.id))
            )
            await ctx.channel.send("Successfully signed up to DM announcements. Run the command again to unsubscribe.")

@commands.check(CustomCooldown(1,2.5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='bal')
async def bal(ctx, user: discord.Member = None):
    if user == None:
        await ctx.channel.send(embed=makeEmbed("Balance", place_value((getcoins(ctx.author)))))
    else:
        await ctx.channel.send(embed=makeEmbed("{}'s Balance".format(user.name), place_value(getcoins(user))))

@commands.check(CustomCooldown(1,2.5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='shop')
async def shop(ctx):
    try:
        fishlim=getinv(ctx.author)['fishlim']
    except:
        fishlim=1
        giveitem(ctx.author, "fishlim", 0)
    await ctx.channel.send(embed=makeEmbed("Shop", """**4 Leaved Clover** | BE SUPER LUCKY WOW | **4,500 coins** | `dd!buy clover`
**Auto Fisher** | Basically a slave | **1,250 coins** | `dd!buy autofish`
**Fish Bait** | Use it to go fishing! | **25 coins** | `dd!buy bait [amount]`
**Fishing Rod Lvl {0}** | Fish {2} fish at once! | **{1} coins** | `dd!buy fishlim`
""".format(str(fishlim+1), place_value(round(1500*(1+1.5)**fishlim)), str(fishlim+1))))
    # msg=""
    # for i in ranks:
    #     msg = msg + "**{0}**: {1} doracoins\n".format(i, ranks[i]["cost"])
    # await ctx.channel.send("Shop", "{}".format(msg))

@commands.check(CustomCooldown(1,2.5, 1, 0, commands.BucketType.user, elements=[]))
@bot.command(name='buy')
async def buy(ctx, rank=None, amount=None):
    if rank == None:
        await ctx.channel.send(embed=makeEmbed("Error", "Please specify something to buy", colour=16711680))
    elif rank in ranks:
        if getcoins(ctx.author) >= ranks[rank]['cost']:
            role = get(bot.get_guild(412536528561242113).roles, id=ranks[rank]['id'])
            givecoins(ctx.author, -int(ranks[rank]['cost']))
            await ctx.author.add_roles(role)
            await ctx.channel.send(embed=makeEmbed("Success", "You've bought {}.".format(rank), colour=1441536))
        else:
            await ctx.channel.send(embed=makeEmbed("Error", "You need to have {} coins".format(str(ranks[rank]['cost'])), colour=16711680))
    # else:
    #     if rank=="custom":
    #         if getcoins(ctx.author) < 40000:
    #             await ctx.channel.send(embed=makeEmbed("Error", "You need to have 40000 coins", colour=16711680))
    #         elif namecolour==None:
    #             if hascustom(ctx.author):
    #                 await ctx.channel.send(embed=makeEmbed("Error", "You already have a custom role", colour=16711680))
    #             else:
    #                 await ctx.channel.send(embed=makeEmbed("Custom Role", "Please run the command again, but with the role name. i.e. `dd!buy custom i am awesome`"))
    #         else:
    #             if hascustom(ctx.author):
    #                 await ctx.channel.send(embed=makeEmbed("Error", "You already have a custom role", colour=16711680))
    #             else:
    #                 givecoins(ctx.author, -40000)
    #                 givecustom(ctx.author)
    #                 nitrorole=get(bot.get_guild(412536528561242113).roles, id=585864265345269799)
    #                 role = await bot.get_guild(412536528561242113).create_role(name=namecolour, reason="Doradroid custom role")
    #                 pos=nitrorole.position
    #                 await role.edit(position=pos, reason="Doradroid custom role - moving to top")
    #                 await ctx.author.add_roles(role)
    #                 await ctx.channel.send(embed=makeEmbed("Success", "You've bought a custom role.", colour=1441536))
    else:
        if rank == "bait":
            if amount == None:
                if getcoins(ctx.author) >= 25:
                    giveitem(ctx.author, "bait", 1)
                    givecoins(ctx.author, -25)
                    await ctx.channel.send(embed=makeEmbed("Success", "You've bought 1 Fish Bait.", colour=1441536))
                else:
                    await ctx.channel.send(embed=makeEmbed("Error", "You need to have 25 coins", colour=16711680))
            else:
                if int(amount)>0:
                    if getcoins(ctx.author) >= 25*int(amount):
                        giveitem(ctx.author, "bait", int(amount))
                        givecoins(ctx.author, -25*int(amount))
                        await ctx.channel.send(embed=makeEmbed("Success", "You've bought {} Fish Bait.".format(amount), colour=1441536))
                    else:
                        await ctx.channel.send(embed=makeEmbed("Error", "You need to have {} coins".format(place_value(int(25*int(amount)))), colour=16711680))
                else:
                    await ctx.channel.send("Don't try to break me smh")
        elif rank == "clover":
            if amount == None or amount == "1":
                if getcoins(ctx.author) >= 4500:
                    giveitem(ctx.author, "clover", 1)
                    givecoins(ctx.author, -4500)
                    await ctx.channel.send(embed=makeEmbed("Success", "You've bought 1 Clover.", colour=1441536))
                else:
                    await ctx.channel.send(embed=makeEmbed("Error", "You need to have 4,500 coins", colour=16711680))
            else:
                if int(amount) > 0:
                    if getcoins(ctx.author) >= 4500*int(amount):
                        giveitem(ctx.author, "clover", int(amount))
                        givecoins(ctx.author, -4500*int(amount))
                        await ctx.channel.send(embed=makeEmbed("Success", "You've bought {} Clovers.".format(amount), colour=1441536))
                    else:
                        await ctx.channel.send(embed=makeEmbed("Error", "You need to have {} coins".format(place_value(int(4500*int(amount)))), colour=16711680))
                else:
                    await ctx.channel.send("Don't try to break me smh")
        elif rank == "autofish":
            if amount == None or amount == "1":
                if getcoins(ctx.author) >= 1250:
                    giveitem(ctx.author, "autofish", 1)
                    givecoins(ctx.author, -1250)
                    await ctx.channel.send(embed=makeEmbed("Success", "You've bought 1 Auto Fisher.", colour=1441536))
                else:
                    await ctx.channel.send(embed=makeEmbed("Error", "You need to have 1,250 coins", colour=16711680))
            else:
                if int(amount) > 0:
                    if getcoins(ctx.author) >= 1250*int(amount):
                        giveitem(ctx.author, "autofish", int(amount))
                        givecoins(ctx.author, -1250*int(amount))
                        await ctx.channel.send(embed=makeEmbed("Success", "You've bought {} Auto Fishers.".format(amount), colour=1441536))
                    else:
                        await ctx.channel.send(embed=makeEmbed("Error", "You need to have {} coins".format(place_value(int(1250*int(amount)))), colour=16711680))
                else:
                    await ctx.channel.send("Don't try to break me smh")
        elif rank == "fishlim":
            try:
                fishlim=getinv(ctx.author)['fishlim']
            except:
                fishlim=1
                giveitem(ctx.author, "fishlim", 0)
            if getcoins(ctx.author) >= round(1500*(1+1.5)**fishlim):
                giveitem(ctx.author, "fishlim", 1)
                givecoins(ctx.author, -round(1500*(1+1.5)**fishlim))
                await ctx.channel.send(embed=makeEmbed("Success", "You've bought Fishing Rod Lvl {}.".format(str(fishlim+1)), colour=1441536))
            else:
                await ctx.channel.send(embed=makeEmbed("Error", "You need to have {} coins".format(str(place_value(round(1500*(1+1.5)**fishlim))), colour=16711680)))
        else:
            await ctx.channel.send(embed=makeEmbed("Error", "{} doesn't exist".format(rank), colour=16711680))

#get(bot.get_guild(412536528561242113).roles, id=416285222452068363) in ctx.author.roles or get(bot.get_guild(412536528561242113).roles, id=412602930601132033) in ctx.author.roles or get(bot.get_guild(412536528561242113).roles, id=412602654741495827) in ctx.author.roles or

@bot.command(name='givemoney')
async def givemoney(ctx, user: discord.Member = None, amount = None):
    global blacklist
    if ctx.author.id in blacklist:
        await ctx.channel.send(embed=makeEmbed("Error", "You are not permitted to use this command", colour=16711680))
    elif ctx.author.id == 330287319749885954:
        if user == None:
            await ctx.channel.send(embed=makeEmbed("Error", "Please specify a member", colour=16711680))
        elif amount == None:
            await ctx.channel.send(embed=makeEmbed("Error", "Please specify an amount of doracoins", colour=16711680))
        else:
            givecoins(user, int(amount))
            await ctx.channel.send(embed=makeEmbed("Success", "Gave {0} {1} doracoins".format(user.name, place_value(int(amount))), colour=1441536))
    else:
        await ctx.channel.send(embed=makeEmbed("Error", "You are not permitted to use this command", colour=16711680))


@bot.command(name='help')
async def help(ctx):
    await ctx.channel.send(embed = makeEmbed("Help", "Doradroid **[help](https://dorami.xyz/bot/help/)**."))

@bot.command(name='beg')
@commands.check(CustomCooldown(1, 20, 1, 10, commands.BucketType.user, elements=[]))
async def beg(ctx):
    reasons = ["ha lol fuck you", "sorry cutie i can't afford it", "ew no ur too stanky", "im too poor", "I'm saving up for JoJo Siwa merch.", "I want to buy food, sorry", "heck you", "lol no", "i cant move help this isnt a joke i actually cant move ples call an ambulance", "i wouldnt give to the likes of you"]
    names = ["Shywess", "A Furry", "An Antifurry", "Belle Delphine",  "Trump", "Elon Musk", "PewDiePie", "Pyrocynical", "Soli", "LazarBeam", "Santa", "Tooth Fairy", "A Brick", "Coronavirus", "Boris Johnson", "My Dog", "A Gay", "Doge", "Florida Man", "DanTDM", "A Homeless Man", "Danny Devito", "Bread Shearan", "A Lonely Neko", "Shrek", "Vladimir Gluten", "John Cena"]
    if random.randint(1,3) != 1:
        amount = random.randint(2, random.randint(15, 40))
        givecoins(ctx.author, amount)
        await ctx.channel.send("**{1}** has given **{2}** {0} coins!".format(amount, random.choice(names), ctx.author.name))
    else:
        await ctx.channel.send("**{1}**: {0}".format(random.choice(reasons), random.choice(names)))


# @bot.command(name='work', aliases=['job'])
# @commands.check(CustomCooldown(1, 15, 1, 43200, commands.BucketType.user, elements=[]))
# async def work(ctx, arg=None):
#     if ctx.message.guild.id!=693821442994995260:
#         await ctx.channel.send("This command only works in the Doradroid server.")
#     elif arg==None:
#         jobid=getinv(ctx.author)['job']
#         if jobid == 0:
#             await ctx.channel.send("You don't have a job, choose from this list")
#             await ctx.channel.send(embed=makeEmbed("Jobs", "Programmer | `dd!work programmer`"))
#     elif arg=="programmer":
#         jobid=getinv(ctx.author)['job']


# @bot.command(name='trivia')
# @commands.check(CustomCooldown(1, 12.5, 1, 12.5, commands.BucketType.user, elements=[]))
# async def trivia(ctx):
#     global triviaanswers
#     r=requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
#     question=r.json()['results'][0]
#     answers=[[question['correct_answer'], "y"], [question['incorrect_answers'][0], "n"], [question['incorrect_answers'][1],"y"], [question['incorrect_answers'][2], "n"]]
#     random.shuffle(answers)
#     a=answers[0][0]
#     b=answers[1][0]
#     c=answers[2][0]
#     d=answers[3][0]
#     correct="a"
#     if answers[0][1] == "y":
#         correct="a"
#     elif answers[2][1] == "y":
#         correct="b"
#     elif answers[3][1] == "y":
#         correct="c"
#     elif answers[4][1] == "y":
#         correct="d"
#     reward=random.randint(1,500)
#     await ctx.channel.send(embed = makeEmbed(question['question'], "**Category**: {0}\n**Difficulty**: {1}\n**Reward**: {6} coins\n**Answers**:\n>>> A. {2}\nB. {3}\nC. {4}\nD. {5}".format(question['category'], question['difficulty'], a, b, c, d, str(reward))))
#     triviaanswers[str(ctx.author.id):{"answer":correct, "reward":reward}]

@bot.command(name='fish')
@commands.check(CustomCooldown(1, 12.5, 1, 12.5, commands.BucketType.user, elements=[]))
async def fishcmd(ctx, rates=None):
    if rates=="rates":
        await ctx.channel.send("**Cyprinodon Diabolis**: 20,000\n**Psychrolutes Marcidus**: 3,000\n**Megamouth Shark**: 1,000\n**Siamese Fighting Fish**: 250\n**Goldfish**: 100\n**Tuna**: 60\n**Northern Pike**: 30\n**Haddock, Cod & Carp**: 20")
    else:
        try:
            bait=getinv(ctx.author)['bait']
        except:
            bait=0
        if bait<=0 and rates != "worth":
            await ctx.channel.send("{}, you have no fish bait. Buy it in the shop!".format(ctx.author.mention))
        else:
            fishing=False
            try:
                int(rates)
                fishing=True
            except:
                pass
            if rates == "max":
                if ctx.author.id == 330287319749885954:
                    bait=getinv(ctx.author)['bait']
                    message = await ctx.channel.send("{0}, ok. Using {1} baits (all of them)".format(ctx.author.mention, str(bait)))
                    giveitem(ctx.author, "bait", -int(bait))
                    fishes=[]
                    for i in range(0, int(bait)):
                        thefish=await fish(ctx)
                        if thefish != None:
                            fishes.append(thefish)
                    amountoffish={"tuna": 0, "psychrolutes":0, "goldfish":0, "carp":0, "cod":0, "haddock":0, "siamese":0, "pike":0, "megamouth":0, "cyprinodon": 0}
                    for i in fishes:
                        amountoffish[i]+=1
                    msg=""
                    fishtypes={"psychrolutes":"Psychrolutes Marcidus :O rare", "goldfish":"Goldfish", "tuna":"Tuna", "carp":"Carp", "cod":"Cod", "haddock":"Haddock", "siamese":"Siamese Fighting Fish", "pike":"Northern Pike", "megamouth":"Megamouth Shark", "cyprinodon": "Cyprinodon Diabolis :OOOO"}
                    amountoffishkeys=sorted(amountoffish, key=str.lower)
                    for i in amountoffishkeys:
                        if amountoffish[i] == 0:
                            pass
                        else:
                            msg=msg+"**{0}**: {1}\n".format(fishtypes[i], str(amountoffish[i]))
                    if msg=="":
                        await message.edit(content="{0}, you caught:\nNothing".format(ctx.author.mention))
                    else:
                        await message.edit(content="{1}, you caught:\n{0}".format(msg, ctx.author.mention))
                else:
                    await ctx.channel.send("This command is for testing purposes only, and so only the owner can use it.")
            elif rates == "worth":
                    message = await ctx.channel.send("{} | Counting fish".format(ctx.author.name))
                    amount = 0
                    inv=getinv(ctx.author)
                    for i in inv:
                        try:
                            amount += fishprices[i]*inv[i]
                        except:
                            pass
                    await asyncio.sleep(1)
                    await message.edit(content="{0} | Your fish would be worth {1} coins.".format(ctx.author.name, place_value(amount)))
            elif fishing == False or int(rates)<=1:
                giveitem(ctx.author, "bait", -1)
                thefish=await fish(ctx)
                if thefish == "cyprinodon":
                    await ctx.channel.send(embed=makeEmbed("{}, you caught a Cyprinodon Diabolis! That's **ULTRA** rare!".format(ctx.author.name), image="https://upload.wikimedia.org/wikipedia/commons/3/37/Cyprinodon_diabolis%2C_males.jpg"))
                elif thefish == "psychrolutes":
                    await ctx.channel.send(embed=makeEmbed("{}, you caught a Psychrolutes Marcidus! That's rare!".format(ctx.author.name), image="https://i.pinimg.com/originals/48/95/71/489571c1fe232dbcef8a9a2e06a8372c.jpg"))
                elif thefish == "megamouth":
                    await ctx.channel.send("{0}, you caught a Megamouth Shark!".format(ctx.author.mention))
                elif thefish == "siamese":
                    await ctx.channel.send("{0}, you caught a Siamese Fighting Fish!".format(ctx.author.mention))
                elif thefish == "goldfish":
                    await ctx.channel.send("{0}, you caught a Goldfish!".format(ctx.author.mention))
                elif thefish == "pike":
                    await ctx.channel.send("{0}, you caught a Northern Pike!".format(ctx.author.mention))
                elif thefish == "haddock":
                    await ctx.channel.send("{0}, you caught a Haddock!".format(ctx.author.mention))
                elif thefish == "cod":
                    await ctx.channel.send("{0}, you caught a Cod!".format(ctx.author.mention))
                elif thefish == "carp":
                    await ctx.channel.send("{0}, you caught a Carp!".format(ctx.author.mention))
                elif thefish == "tuna":
                    await ctx.channel.send("{0}, you caught a Tuna!".format(ctx.author.mention))
                elif thefish == None:
                    await ctx.channel.send("{0}, you didn't get a bite.".format(ctx.author.mention))
            else:
                try:
                    fishlim=getinv(ctx.author)['fishlim']
                except:
                    fishlim=1
                    giveitem(ctx.author, "fishlim", 0)
                if int(rates)<=0:
                    await ctx.channel.send("{}, you can't fish less than once.".format(ctx.author.mention))
                elif int(rates)>fishlim:
                    await ctx.channel.send("{0}, your fishing rod only lets you fish {1} fish at a time. Upgrade it at the shop!".format(ctx.author.mention, str(fishlim)))
                else:
                    bait=getinv(ctx.author)['bait']
                    if bait >= int(rates):
                        giveitem(ctx.author, "bait", -int(rates))
                        fishes=[]
                        for i in range(0, int(rates)):
                            thefish=await fish(ctx)
                            if thefish != None:
                                fishes.append(thefish)
                        amountoffish={"tuna": 0, "psychrolutes":0, "goldfish":0, "carp":0, "cod":0, "haddock":0, "siamese":0, "pike":0, "megamouth":0, "cyprinodon": 0}
                        for i in fishes:
                            amountoffish[i]+=1
                        msg=""
                        fishtypes={"psychrolutes":"Psychrolutes Marcidus :O rare", "goldfish":"Goldfish", "tuna":"Tuna", "carp":"Carp", "cod":"Cod", "haddock":"Haddock", "siamese":"Siamese Fighting Fish", "pike":"Northern Pike", "megamouth":"Megamouth Shark", "cyprinodon": "Cyprinodon Diabolis :OOOO"}
                        amountoffishkeys=sorted(amountoffish, key=str.lower)
                        for i in amountoffishkeys:
                            if amountoffish[i] == 0:
                                pass
                            else:
                                msg=msg+"**{0}**: {1}\n".format(fishtypes[i], str(amountoffish[i]))
                        if msg=="":
                            await ctx.channel.send("{0}, you caught:\nNothing".format(ctx.author.mention))
                        else:
                            await ctx.channel.send("{1}, you caught:\n{0}".format(msg, ctx.author.mention))
                    else:
                        await ctx.channel.send("{}, you don't have enough bait!".format(ctx.author.mention))



@bot.command(name='inventory', aliases=["inv"])
@commands.check(CustomCooldown(1, 5, 1, 0, commands.BucketType.user, elements=[]))
async def inventory(ctx, user: discord.Member = None):
    if user==None:
        inv = getinv(ctx.author)
    else:
        inv = getinv(user)

    if inv == {}:
        if user==None:
            await ctx.channel.send(embed=makeEmbed("You don't have anything in your inventory", footer="Fucking pleb"))
        else:
            await ctx.channel.send(embed=makeEmbed("{1} doesn't have anything in their inventory".format(user.name), footer="Fucking pleb"))
    else:
        msg=""
        invkeys=sorted(inv, key=str.lower)
        for i in invkeys:
            if inv[i] != 0:
                if i == "psychrolutes":
                    msg=msg+"**Psychrolutes Marcidus <:marcidus:697073971518242908>**: {}\n".format(place_value(inv[i]))
                elif i == "megamouth":
                    msg=msg+"**Megamouth Shark <:megamouth:697073969861230684>**: {}\n".format(place_value(inv[i]))
                elif i == "siamese":
                    msg=msg+"**Siamese Fighting Fish <:siamese:697073971576832060>**: {}\n".format(place_value(inv[i]))
                elif i == "goldfish":
                    msg=msg+"**Goldfish <:goldfish:697073971824164865>**: {}\n".format(place_value(inv[i]))
                elif i == "pike":
                    msg=msg+"**Northern Pike <:pike:697073971685883964>**: {}\n".format(place_value(inv[i]))
                elif i == "cod":
                    msg=msg+"**Cod <:cod:697073970679251074>**: {}\n".format(place_value(inv[i]))
                elif i == "carp":
                    msg=msg+"**Carp <:carp:697073971816038421>**: {}\n".format(place_value(inv[i]))
                elif i == "haddock":
                    msg=msg+"**Haddock <:haddock:697073970217746624>**: {}\n".format(place_value(inv[i]))
                elif i == "bait":
                    msg=msg+"**Fish Bait <:bait:697073969701978112>**: {}\n".format(place_value(inv[i]))
                elif i == "cyprinodon":
                    msg=msg+"**Cyprinodon Diabolis <:pup:697073971803455508>**: {}\n".format(place_value(inv[i]))
                elif i == "tuna":
                    msg=msg+"**Tuna <:tuna:697073967797895259>**: {}\n".format(place_value(inv[i]))
                elif i == "fishlim":
                    msg=msg+"**Fishing Rod Lvl {} <:rod:697073970121408532>**\n".format(place_value(inv[i]))
                elif i == "autofish":
                    msg=msg+"**Auto Fisher <:rod:697073970121408532>**: {} (`dd!use autofish`)\n".format(place_value(inv[i]))
                elif i == "clover":
                    msg=msg+"**4 Leafed Clover <:clover:697088691159564389>**: {} (`dd!use clover`)\n".format(place_value(inv[i]))
                else:
                    msg=msg+"**__Unknown Item__ :grey_question:**: {}\n".format(place_value(inv[i]))
        if user == None:
            await ctx.channel.send(embed=makeEmbed("{}'s Inventory".format(ctx.author.name), msg))
        else:
            await ctx.channel.send(embed=makeEmbed("{}'s Inventory".format(user.name), msg))

@bot.command(name='sell')
@commands.check(CustomCooldown(1,15, 1, 0, commands.BucketType.user, elements=[]))
async def sell(ctx):
    message = await ctx.channel.send("{} | Selling all your fish".format(ctx.author.name))
    amount = 0
    inv=getinv(ctx.author)
    for i in inv:
        try:
            amount += fishprices[i]*inv[i]
            giveitem(ctx.author, i, -inv[i])
        except:
            pass
    await asyncio.sleep(1)
    givecoins(ctx.author, amount)
    await message.edit(content="{0} | You got {1} coins!".format(ctx.author.name, place_value(amount)))

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
            try:
                msg=msg+":first_place: {0}: {1} doracoins\n".format(bot.get_user(int(i[1])).name, place_value(i[2]))
            except:
                msg=msg+":first_place: `USER LEFT`: {0} doracoins\n".format(place_value(i[2]))
        elif j == 2:
            try:
                msg=msg+":second_place: {0}: {1} doracoins\n".format(bot.get_user(int(i[1])).name, place_value(i[2]))
            except:
                msg=msg+":second_place: `USER LEFT`: {0} doracoins\n".format(place_value(i[2]))
        elif j == 3:
            try:
                msg=msg+":third_place: {0}: {1} doracoins\n".format(bot.get_user(int(i[1])).name, place_value(i[2]))
            except:
                msg=msg+":third_place: `USER LEFT`: {0} doracoins\n".format(place_value(i[2]))
        else:
            try:
                msg=msg+"{0}) {1}: {2} doracoins\n".format(str(j), bot.get_user(int(i[1])).name, place_value(i[2]))
            except:
                msg=msg+"{0}) {1}: {2} doracoins\n".format(str(j), "`USER LEFT`", place_value(i[2]))
    await ctx.channel.send(embed=makeEmbed("Leaderboard", msg, footer="sweats"))

@bot.command(name='gamble', aliases=["bet"])
@commands.check(CustomCooldown(1, 15, 1, 0, commands.BucketType.user, elements=[]))
async def gamble(ctx, amount=None):
    if amount == None:
        await ctx.channel.send(embed=makeEmbed("Error", "Please specify an amount of coins", colour=16711680))
    elif int(amount) <= 0:
        await ctx.channel.send(embed=makeEmbed("Error", "Choose a number higher then 0", colour=16711680))
    elif int(amount) > getcoins(ctx.author):
        await ctx.channel.send(embed=makeEmbed("Error", "You don't have {} coins".format(str(amount)), colour=16711680))
    else:
        lucky=False
        if str(ctx.author.id) in activeitems:
            if "clover" in activeitems[str(ctx.author.id)]:
                lucky=True
        givecoins(ctx.author, -int(amount))
        message = await ctx.channel.send("{0}'s game".format(ctx.author.name))
        deck = doc.DeckOfCards()
        card = deck.give_random_card()
        card2 = deck.give_random_card()
        suits={0:"♠", 1:"♥", 2:"♦", 3:"♣"}
        values={1:"A", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"10", 11:"J", 12:"Q", 13:"K"}
        if lucky:
            userval=card.value+3
            if userval>13:
                userval=13
        else:
            userval=card.value
        await asyncio.sleep(1)
        await message.edit(content="{1}'s game\nYou: {0}".format(suits[card.suit]+values[userval],ctx.author.name))
        await asyncio.sleep(1)
        await message.edit(content="{2}'s game\nYou: {0}\nDoradroid: {1}".format(suits[card.suit]+values[userval],suits[card2.suit]+values[card2.value],ctx.author.name))
        await asyncio.sleep(1)
        if userval > card2.value:
            await message.edit(content="{2}'s game\nYou: {0}\nDoradroid: {1}\n**You won twice your bet!**".format(suits[card.suit]+values[userval],suits[card2.suit]+values[card2.value],ctx.author.name))
            givecoins(ctx.author, int(amount)*2)
        elif userval < card2.value:
            await message.edit(content="{2}'s game\nYou: {0}\nDoradroid: {1}\n**You lost!**".format(suits[card.suit]+values[userval],suits[card2.suit]+values[card2.value],ctx.author.name))
        else:
            givecoins(ctx.author, int(amount))
            await message.edit(content="{2}'s game\nYou: {0}\nDoradroid: {1}\n**You drew! Your coins were refunded.**".format(suits[card.suit]+values[userval],suits[card2.suit]+values[card2.value],ctx.author.name))

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
            await ctx.channel.send(embed=makeEmbed("Success", "Gave {0} {1} coins".format(user.name, place_value(int(amount))), colour=1441536))
        else:
            await ctx.channel.send(embed=makeEmbed("Error", "You don't have {} coins".format(place_value(int(amount))), colour=16711680))

bot.run(TOKEN)
