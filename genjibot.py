from discord.ext import commands
import pyimgur
import requests
import shutil
import os
import grabd
from dotenv import load_dotenv
from grabd import text_vals, parse_vals


#load environment variables
load_dotenv()

client = commands.Bot(command_prefix='!')
CLIENT_ID = os.getenv("IMGUR_TOKEN")


@client.event
async def on_ready():
    print('ready')


async def run_calc(stat_list, value_list, gear_options):
    return grabd.run(stat_list, value_list, gear_options)

@client.command()
async def gear(ctx):
    if ctx.author == client.user:
        return

    await ctx.send (
            "Do you need to change the defaults?\nThe defaults are 85, purple ONLY +15 is supported\n(y/n)"
    )
    gear_options = []
    def check(m):
        return (m.content == 'y' or m.content == 'n') and m.channel == ctx.channel and m.author == ctx.author

    msg = await client.wait_for('message', check=check)

    if (msg.content == 'y'):
        #Grab gear lvl, geartype, gear enhance
        await ctx.send("Please enter the gear level, gear type/color (options below) follwed by a space")
        await ctx.send(f"Gear level: {text_vals['gear-levels']}, Gear-color: {text_vals['gear-type']}")
        def check1(m):
            op1_list = m.content.split(' ')
            if op1_list[0] in text_vals['gear-levels'] and op1_list[1] in text_vals['gear-type']:
                def_lvl = "lv" + op1_list[0]
                if op1_list[1] != 'purple':
                    def_geartype = "g" + op1_list[1]
                else:
                    def_geartype = "gpink"
                gear_options.append(def_lvl)
                gear_options.append(def_geartype)
                return True
            return False
        msg = await client.wait_for('message', check=check1)
        await ctx.send(f"Gear level and gear type changed: {msg.content} +15")
            
            
        arglist = parse_vals['supported_stats']
        await ctx.send(f"Please enter 4 stats you wish to calculate: {arglist}")

        def check2(m):
            response_list = set(m.content.split(' '))
            return len(response_list) == 4 and m.channel == ctx.channel and set(response_list).issubset(set(arglist)) and m.author == ctx.author
        msg = await client.wait_for('message', check=check2)
        await ctx.send(f"Stats received: {msg.content}")



        await ctx.send(f"Please enter the corresponding values for the stats above: {msg.content}")

        def check3(m):
            return m.channel == ctx.channel and len(m.content.split(' ')) == 4 and m.author == ctx.author
        msg2 = await client.wait_for('message', check=check3)
        stats_list = zip(msg.content.split(' '), msg2.content.split(' '))
        stats_list = dict(stats_list)

        await ctx.send(f"The stats received were: {stats_list}\n**Calculating**")
        text = await run_calc(msg.content.split(' '), msg2.content.split(' '), gear_options)
        await ctx.send(f"{ctx.author.mention}\n{text}")



@client.command(aliases=['Cry', 'cry'])
async def _cry(ctx):
    await ctx.send("Jickie left me. Now I'm all alone... :FeelsStrongMan:")


@client.command()
async def upload(ctx, *args):
    if not args:
        print("NO FILE NAME FOUND")
        await ctx.send("Missing unit name! Enter a unit name after !upload")
        return

    try:
        url = ctx.message.attachments[0].url
    except IndexError:
        print("Error: No attachments")
        await ctx.send("No image submitted")

    else:
        if url[0:26] == "https://cdn.discordapp.com":
            r = requests.get(url, stream=True)
            imageName = str(ctx.author.name) + "_" + args[0] + ".jpg"
            with open("unit_links.txt") as file:
                for line in file:
                    if line.split(': ')[0] == (str(ctx.author.name) + "_" + args[0]):
                        await ctx.send("Unit already exists!")
                        return

            with open(imageName, 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)

            PATH = imageName
            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(PATH, title=str(ctx.author.name) + "_" + args[0])
            os.remove(imageName)
            f = open("unit_links.txt", "a")
            f.write(str(ctx.author.name).lower() + "_" + args[0].lower() + ": " + uploaded_image.link + "\n")
            f.close()
            await ctx.send("Unit added!")


@client.command()
async def getunits(ctx, *args):
    names = []
    units = []

    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author

    if not args:

        # asks user who, then lists out names
        await ctx.send("Whose units would you like to look at?")
        with open("unit_links.txt") as file:
            for line in file:
                names.append(line.split('_')[0])

        # makes it so names are unique
        for name in set(names):
            print(name)
            await ctx.send("- " + name)

        # user input names
        user = await client.wait_for("message", check=check)

        # checks if user inputted correctly
        if user.content not in names:
            await ctx.send(f"User not found!")
            return
        else:
            await ctx.send(f"And what unit would you like to look at?")

        # opens text file and adds unit to units array
        with open("unit_links.txt") as file:
            for line in file:
                if line.split('_')[0] == user.content:
                    word = line
                    units.append(word[word.find('_') + 1: word.find(':')])

        # print units from units array
        await ctx.send(units)

        unit = await client.wait_for("message", check=check)

        if unit.content not in units:
            await ctx.send("No unit found!")
            return

        with open("unit_links.txt") as file:
            for line in file:
                if user.content + "_" + unit.content in line:
                    print(line)
                    await ctx.send(
                        f"Hera ya go! Here's " + user.content + "'s " + unit.content + ": " + line.split(': ')[1])
                    break

    if len(args) == 1 and args[0] == "help":
        await ctx.send(f"Format is: \"!getunits <name> <unit>\"     OR      \"!getunits\"")
        return

    if len(args) == 1:
        with open("unit_links.txt") as file:
            for line in file:
                names.append(line.split('_')[0])

        if args[0] not in names:
            await ctx.send(f"User not found!")
            return
        else:
            await ctx.send(f"And what unit would you like to look at?")

        # opens text file and adds unit to units array
        with open("unit_links.txt") as file:
            for line in file:
                if line.split('_')[0] == args[0]:
                    word = line
                    units.append(word[word.find('_') + 1: word.find(':')])

        # print units from units array
        await ctx.send(units)

        unit = await client.wait_for("message", check=check)

        if unit.content not in units:
            await ctx.send("No unit found!")
            return

        with open("unit_links.txt") as file:
            for line in file:
                if args[0] + "_" + unit.content in line:
                    print(line)
                    await ctx.send(
                        f"Hera ya go! Here's " + args[0] + "'s " + unit.content + ": " + line.split(': ')[1])
                    break

    if len(args) == 2:
        with open("unit_links.txt") as file:
            for line in file:
                names.append(line.split('_')[0])

        if args[0] not in names:
            await ctx.send(f"User not found!")
            return

            # opens text file and adds unit to units array
        with open("unit_links.txt") as file:
            for line in file:
                if line.split('_')[0] == args[0]:
                    word = line
                    units.append(word[word.find('_') + 1: word.find(':')])

        if args[1] not in units:
            await ctx.send("No unit found!")
            return

        with open("unit_links.txt") as file:
            for line in file:
                if args[0] + "_" + args[1] in line:
                    print(line)
                    await ctx.send(
                        f"Hera ya go! Here's " + args[0] + "'s " + args[1] + ": " + line.split(': ')[1])
                    break


@client.command()
async def removeunit(ctx, *args):
    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author

    units = []
    if not args:
        await ctx.send("Which unit would you like to remove?")
        # opens text file and adds unit to units array

        with open("unit_links.txt") as file:
            for line in file:
                if line.split('_')[0] == ctx.author.name:
                    word = line
                    units.append(word[word.find('_') + 1: word.find(':')])

        # print units from units array
        await ctx.send(units)

        unit = await client.wait_for("message", check=check)

        imagename = str(ctx.author.name) + "_" + str(unit.content) + ": "

        with open('unit_links.txt') as f:
            if imagename in f.read():
                await ctx.send("Unit removed")
                with open("unit_links.txt", "r") as fi:
                    lines = fi.readlines()
                with open("unit_links.txt", "w") as fi:
                    for line in lines:
                        if line.split('https:')[0] != imagename:
                            fi.write(line)
                return
        await ctx.send("Unit not found")
        return

    if len(args) == 1 and args[0] == "help":
        await ctx.send("!removeunit     OR      !removeunit <unit name>")
        return

    if len(args) == 1:
        imagename = str(ctx.author.name) + "_" + args[0] + ": "

        with open('unit_links.txt') as f:
            if imagename in f.read():
                await ctx.send("Unit removed")
                with open("unit_links.txt", "r") as fi:
                    lines = fi.readlines()
                with open("unit_links.txt", "w") as fi:
                    for line in lines:
                        if line.split('https:')[0] != imagename:
                            fi.write(line)
                return
        await ctx.send("Unit not found")
        return
    else:
        await ctx.send("Error! Use \"!removeunit help\" for usage")
        return


client.run(os.getenv('GENJI_TOKEN'))
