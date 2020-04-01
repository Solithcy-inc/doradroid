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
import slotmachine as sm
#############
global cursor, whitelist, ranks
fishprices = {"psychrolutes":17500, "goldfish":750, "carp":10, "cod":10, "haddock":10, "siamese":1000, "pike":500, "megamouth":3750, "cyprinodon": 75000}
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
    elif ctx.guild is False:
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
            if ctx.channel.id in [574247398855933963, 694220899246932101, 412670226321244161, 694532375480107100]:
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

def giveitem(user, item, amount):
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
        webhook = Webhook.partial(694219649331626075, 'O1LHhL3hwNrFUe2k2HQst_sGIiPbO5J96nu-57Ur8naHe6FAVKey7Xt8owSplSUQcbyJ', adapter=RequestsWebhookAdapter())
        webhook.send(embed=makeEmbed("New user", "{} made an inventory".format(user)))
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
        dict2 = {0:"", 1:"", 2:"carp", 3:"cod", 4:"bait", 5:"goldfish", 6:"haddock", 7:"megamouth", 8:"pike", 9:"psychrolutes", 10:"siamese", 11:"cyprinodon"}
        for i in records[0]:
            if j in [0,1]:
                pass
            else:
                if i != 0:
                    empty=False
                dict1[dict2[j]]=i
            j+=1
        if empty:
            return {}
        else:
            return dict1
    else:
        return {}

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
    await ctx.channel.send(embed=makeEmbed("Shop", """Fish Bait | Use it to go fishing! | 17 coins | `dd!buy bait [amount]`
"""))
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
                if getcoins(ctx.author) >= 17:
                    giveitem(ctx.author, "bait", 1)
                    givecoins(ctx.author, -17)
                    await ctx.channel.send(embed=makeEmbed("Success", "You've bought 1 Fish Bait.", colour=1441536))
                else:
                    await ctx.channel.send(embed=makeEmbed("Error", "You need to have 17 coins", colour=16711680))
            else:
                if getcoins(ctx.author) >= 17*int(amount):
                    giveitem(ctx.author, "bait", int(amount))
                    givecoins(ctx.author, -17*int(amount))
                    await ctx.channel.send(embed=makeEmbed("Success", "You've bought {} Fish Bait.".format(amount), colour=1441536))
                else:
                    await ctx.channel.send(embed=makeEmbed("Error", "You need to have {} coins".format(str(17*int(amount))), colour=16711680))
        else:
            await ctx.channel.send(embed=makeEmbed("Error", "{} doesn't exist".format(rank), colour=16711680))

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

@bot.command(name='fish')
@commands.check(CustomCooldown(1, 10, 1, 10, commands.BucketType.user, elements=[]))
async def fish(ctx, rates=None):
    if rates=="rates":
        await ctx.channel.send("**Cyprinodon Diabolis**: 75,000\n**Psychrolutes Marcidus**: 17,500\n**Megamouth Shark**: 3,750\n**Siamese Fighting Fish**: 1,000\n**Goldfish**: 750\n**Northern Pike**: 500\n**Haddock, Cod & Carp**: 10")
    else:
        try:
            bait=getinv(ctx.author)['bait']
        except:
            bait=0
        if bait<=0:
            await ctx.channel.send("{}, you have no fish bait. Buy it in the shop!".format(ctx.author.mention))
        else:
            giveitem(ctx.author, "bait", -1)
            chance=random.randint(1, 100000)
            if chance <= 1:
                print("Cyprinodon Diabolis captured")
                giveitem(ctx.author, "cyprinodon", 1)
                await ctx.channel.send(embed=makeEmbed("{}, you caught a Cyprinodon Diabolis! That's **ULTRA** rare!".format(ctx.author.mention), image="https://upload.wikimedia.org/wikipedia/commons/3/37/Cyprinodon_diabolis%2C_males.jpg"))
            else:
                chance=random.randint(1, 100000)
                if chance <= 150:
                    print("Psychrolutes Marcidus captured")
                    giveitem(ctx.author, "psychrolutes", 1)
                    await ctx.channel.send(embed=makeEmbed("{}, you caught a Psychrolutes Marcidus! That's rare!".format(ctx.author.mention), image="https://i.pinimg.com/originals/48/95/71/489571c1fe232dbcef8a9a2e06a8372c.jpg"))
                else:
                    chance=random.randint(1, 100000)
                    if chance <= 2500:
                        giveitem(ctx.author, "megamouth", 1)
                        await ctx.channel.send("{}, you caught a Megamouth Shark!".format(ctx.author.mention))
                    else:
                        chance=random.randint(1, 100000)
                        if chance <= 5000:
                            giveitem(ctx.author, "siamese", 1)
                            await ctx.channel.send("{}, you caught a Siamese Fighting Fish!".format(ctx.author.mention))
                        else:
                            chance=random.randint(1, 100000)
                            if chance <= 10000:
                                giveitem(ctx.author, "goldfish", 1)
                                await ctx.channel.send("{}, you caught a Goldfish!".format(ctx.author.mention))
                            else:
                                chance=random.randint(1, 100000)
                                if chance <= 15000:
                                    giveitem(ctx.author, "pike", 1)
                                    await ctx.channel.send("{}, you caught a Northern Pike!".format(ctx.author.mention))
                                else:
                                    chance=random.randint(1, 100000)
                                    if chance <= 70000:
                                        types=[['cod', 'Cod'],['carp', 'Carp'],['haddock', 'Haddock']]
                                        thetype=random.choice(types)
                                        giveitem(ctx.author, thetype[0], 1)
                                        await ctx.channel.send("{1}, you caught a {0}!".format(thetype[1], ctx.author.mention))
                                    else:
                                        await ctx.channel.send("{}, you didn't get a bite.".format(ctx.author.mention))

@bot.command(name='inventory', aliases=["inv"])
@commands.check(CustomCooldown(1, 5, 1, 0, commands.BucketType.user, elements=[]))
async def inventory(ctx):
    inv = getinv(ctx.author)
    if inv == {}:
        await ctx.channel.send(embed=makeEmbed("You don't have anything in your inventory", footer="Fucking pleb"))
    else:
        msg=""
        for i in inv:
            if inv[i] != 0:
                if i == "psychrolutes":
                    msg=msg+"**Psychrolutes Marcidus**: {}\n".format(inv[i])
                elif i == "megamouth":
                    msg=msg+"**Megamouth Shark**: {}\n".format(str(inv[i]))
                elif i == "siamese":
                    msg=msg+"**Siamese Fighting Fish**: {}\n".format(str(inv[i]))
                elif i == "goldfish":
                    msg=msg+"**Goldfish**: {}\n".format(str(inv[i]))
                elif i == "pike":
                    msg=msg+"**Northern Pike**: {}\n".format(str(inv[i]))
                elif i == "cod":
                    msg=msg+"**Cod**: {}\n".format(str(inv[i]))
                elif i == "carp":
                    msg=msg+"**Carp**: {}\n".format(str(inv[i]))
                elif i == "haddock":
                    msg=msg+"**Haddock**: {}\n".format(str(inv[i]))
                elif i == "bait":
                    msg=msg+"**Fish Bait**: {}\n".format(str(inv[i]))
                elif i == "cyprinodon":
                    msg=msg+"**Cyprinodon Diabolis**: {}\n".format(str(inv[i]))
                else:
                    msg=msg+"**__Unknown Item__**: {}\n".format(str(inv[i]))
        await ctx.channel.send(embed=makeEmbed("{}'s Inventory".format(ctx.author.name), msg))

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
    await message.edit(content="{0} | You got {1} coins!".format(ctx.author.name, str(amount)))

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
@commands.check(CustomCooldown(1, 15, 1, 0, commands.BucketType.user, elements=[]))
async def gamble(ctx, amount=None):
    if amount == None:
        await ctx.channel.send(embed=makeEmbed("Error", "Please specify an amount of coins", colour=16711680))
    elif int(amount) <= 0:
        await ctx.channel.send(embed=makeEmbed("Error", "Choose a number higher then 0", colour=16711680))
    elif int(amount) > getcoins(ctx.author):
        await ctx.channel.send(embed=makeEmbed("Error", "You don't have {} coins".format(str(amount)), colour=16711680))
    else:
        givecoins(ctx.author, -int(amount))
        message = await ctx.channel.send("{0}'s game".format(ctx.author.name))
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
