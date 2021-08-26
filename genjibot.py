from discord.ext import commands
import discord
import pyimgur
import requests
import shutil
import os
import grabd
from dotenv import load_dotenv
from grabd import text_vals, parse_vals
import dropbox
import asyncio


#load environment variables
load_dotenv()

client = commands.Bot(command_prefix='!')
CLIENT_ID = os.getenv("IMGUR_TOKEN")
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Downloads file from dropbox
def download_file(tempfile, filename):
    metadata = dbx.files_download_to_file(tempfile, filename)
    return metadata

# Uploads a file to dropbox
def upload_file(filename, localfile):
    with open(localfile, "rb") as f:
        dbx.files_upload(f.read(), filename, mute=True)


@client.event
async def on_ready():
    print('ready')
    
client.remove_command('help')


@client.command()
async def help(ctx, *argument):
    if not argument:
        await ctx.send("```Commands:"
                       "\n !cry             wah"
                       "\n !gear            Turns on interactive mode"
                       "\n !help            Shows this message"
                       "\n Rebels Only:"
                       "\n !unitbuilds        !help unitbuilds      for more info"
                       "\n !upload          !help upload        for more info```")
        return
    if argument[0] == "unitbuilds" and len(argument) == 1:
        await ctx.send("```Shows an uploaded unit's builds. \n"
                       "Usage: \n"
                       "!unitbuilds \n```")
        return
    if argument[0] == "upload" and len(argument) == 1:
        await ctx.send("```Uploads a screenshot of an unit to the album. \n"
                       "Usage: \n"
                       "    upload an image onto discord with the following description: \n"
                       "    !upload```")
        return

    

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



@client.command()
async def cry(ctx):
    await ctx.send("Jickie left me. Now I'm all alone... <:FeelsStrongMan:730679903812321321>")

    
@client.command()
async def upload(ctx):
    def checkinput(m):
        return m.channel == ctx.channel and m.author == ctx.author

    namesindb = []

    elements = ["Fire", "Ice", "Earth", "Light", "Dark"]

    gearset4 = ["Speed", "Counter", "Attack", "Destruction", "Lifesteal", "Rage", "Revenge", "Injury", "2-set",
                "Cancel"]
    gearset2 = ["Crit", "Hit", "Health", "Defense", "Resist", "Immunity", "Unity", "Penetration", "None", "Cancel"]

    # Asks what the element they would like to upload first
    await ctx.send(">>> What element is the unit you would like to upload?")

    element_block = ""
    for i in range(len(elements)):
        element_block += (str(i + 1) + ": " + elements[i].title() + "\n")
    await ctx.send(f"```{element_block}```")

    element_choice = await client.wait_for("message", check=checkinput)

    if element_choice.content.isdigit():
        if int(element_choice.content) <= len(elements) and int(element_choice.content) != 0:
            elementselection = elements[int(element_choice.content) - 1]
        else:
            await ctx.send(">>> Invalid number")
            return
    else:
        if element_choice.content.title() in elements:
            elementselection = element_choice.content.title()
        else:
            await ctx.send(">>> No unit found")
            return

    await ctx.send(f"You have chosen {elementselection}")

    download_file("tempunitinfo.txt", "/unit_info.txt")

    # populate namesindb array
    with open("tempunitinfo.txt") as file:
        for line in file:
            start = ":"
            end = ";"
            elementinfile = (line[line.find(start) + len(start):line.rfind(end)]).strip().title()
            if elementselection == elementinfile:
                namesindb.append(str(line.split(':')[0]).lower())

    os.remove("tempunitinfo.txt")
    stringofnames = ""

    sorted(namesindb)
    # makes a string for list of units
    for i in range(len(namesindb)):
        stringofnames += (str(i + 1) + ": " + namesindb[i].title() + "\n")

    await ctx.send(">>> What unit build would you like to upload?")
    await ctx.send(f"```{stringofnames}```")
    # user input unit name
    unit = await client.wait_for("message", check=checkinput)

    # User picks unit or types it out
    if unit.content.isdigit():
        if int(unit.content) <= len(namesindb) and int(unit.content) != 0:
            unitselection = namesindb[int(unit.content) - 1]
        else:
            await ctx.send(">>> Invalid number")
            return
    else:
        if unit.content.lower() in namesindb:
            unitselection = unit.content.title()
        else:
            await ctx.send(">>> No unit found")
            return

    # string for printing out 4-set array and 2-set array
    listoutgearset4 = ""
    listoutgearset2 = ""
    for i in range(len(gearset4)):
        listoutgearset4 += (str(i + 1) + ": " + gearset4[i] + "\n")
    for i in range(len(gearset2)):
        listoutgearset2 += (str(i + 1) + ": " + gearset2[i] + "\n")

    # if user input is in the units
    if unitselection.lower() in namesindb:
        found = True
    else:
        found = False

    # if its not in units, reply that it is not found
    if not found:
        await ctx.send(f"Unit \"{unitselection.title()}\" not found in database")
        return
    else:
        # else prompt sets to choose from
        await ctx.send(">>> Enter the first set: ")
        await ctx.send(f"```{listoutgearset4}```")

    # user picks out 4-set choice
    firstsetselection = await client.wait_for("message", check=checkinput)

    # User picks first 4 set choice, either through a number or typing it out
    if firstsetselection.content.isdigit():
        # if the selection is a number, and is in the range between len() and 1,
        # set decision, otherwise exit from command
        if int(firstsetselection.content) <= len(gearset4) and int(firstsetselection.content) != 0:
            setselection4 = gearset4[int(firstsetselection.content) - 1]
        else:
            await ctx.send(">>> Invalid number")
            return
    else:
        # if the user inputs a string, check if its in the array, else exit from command
        if firstsetselection.content.title() in gearset4:
            setselection4 = firstsetselection.content.title()
        else:
            await ctx.send(">>> No set found")
            return

    # if user chooses cancel, print goodbye and exit
    if setselection4 == gearset4[9]:
        await ctx.send(">>> Goodbye!")
        return

    # if user picks 2 set first
    if setselection4 == gearset4[8]:
        await ctx.send(">>> What is the first set? ")
        await ctx.send(f"```{listoutgearset2}```")
        twosetselection1 = await client.wait_for("message", check=checkinput)
        # ---
        # User picks first 2 set choice, either through a number or typing it out
        if twosetselection1.content.isdigit():
            # if the selection is a number, and is in the range between len() and 1,
            # set decision, otherwise exit from command
            if int(twosetselection1.content) <= len(gearset2) and int(twosetselection1.content) != 0:
                first2setselection = gearset2[int(twosetselection1.content) - 1]
            else:
                await ctx.send(">>> Invalid number")
                return
        else:
            # if the user inputs a string, check if its in the array, else exit from command
            if twosetselection1.content.title() in gearset2:
                first2setselection = twosetselection1.content.title()
            else:
                await ctx.send(">>> No set found")
                return
        # if user chooses cancel, print goodbye and exit
        if first2setselection == gearset2[9]:
            await ctx.send(">>> Goodbye!")
            return
        if first2setselection == gearset2[8] or first2setselection.lower() == "none":
            first2setselection = " "
        # ---
        await ctx.send(">>> What is the second set? ")
        await ctx.send(f"```{listoutgearset2}```")
        twosetselection2 = await client.wait_for("message", check=checkinput)
        # ---
        # User picks second 2 set choice, either through a number or typing it out
        if twosetselection2.content.isdigit():
            # if the selection is a number, and is in the range between len() and 1,
            # set decision, otherwise exit from command
            if int(twosetselection2.content) <= len(gearset2) and int(twosetselection2.content) != 0:
                second2setselection = gearset2[int(twosetselection2.content) - 1]
            else:
                await ctx.send(">>> Invalid number")
                return
        else:
            # if the user inputs a string, check if its in the array, else exit from command
            if twosetselection2.content.title() in gearset2:
                second2setselection = twosetselection2.content.title()
            else:
                await ctx.send(">>> No set found")
                return
        # if user chooses cancel, print goodbye and exit
        if second2setselection == gearset2[9]:
            await ctx.send(">>> Goodbye!")
            return
        if second2setselection == gearset2[8] or second2setselection.lower() == "none":
            second2setselection = " "
        # ---
        await ctx.send(">>> What is the third set? ")
        await ctx.send(f"```{listoutgearset2}```")
        twosetselection3 = await client.wait_for("message", check=checkinput)
        # ---
        # User picks third 2 set choice, either through a number or typing it out
        if twosetselection3.content.isdigit():
            # if the selection is a number, and is in the range between len() and 1,
            # set decision, otherwise exit from command
            if int(twosetselection3.content) <= len(gearset2) and int(twosetselection3.content) != 0:
                third2setselection = gearset2[int(twosetselection3.content) - 1]
            else:
                await ctx.send(">>> Invalid number")
                return
        else:
            # if the user inputs a string, check if its in the array, else exit from command
            if twosetselection3.content.title() in gearset2:
                third2setselection = twosetselection3.content.title()
            else:
                await ctx.send(">>> No set found")
                return
        # if user chooses cancel, print goodbye and exit
        if third2setselection == gearset2[9]:
            await ctx.send(">>> Goodbye!")
            return
        if third2setselection == gearset2[8] or third2setselection.lower() == "none":
            third2setselection = " "
        # ---

        # makes a string based off of user's choices
        temparray = [first2setselection, second2setselection, third2setselection]
        final2setselection = ""
        for i in range(1, len(temparray)):
            if temparray[i - 1] != " ":
                final2setselection += f"{temparray[i - 1]} + "
        if temparray[2] != " ":
            final2setselection += temparray[2]
        else:
            final2setselection = final2setselection[:-2]

        finalsetselection = final2setselection

        await ctx.send(f">>> You have picked " + final2setselection)
    else:
        await ctx.send(f">>> You have picked " + setselection4)
        await ctx.send(">>> Enter second set: ")
        await ctx.send(f"```{listoutgearset2}```")
        secondsetselection = await client.wait_for("message", check=checkinput)
        # User picks first 2 set choice, either through a number or typing it out
        if secondsetselection.content.isdigit():
            if int(secondsetselection.content) <= len(gearset2) and int(secondsetselection.content) != 0:
                setselection2 = gearset2[int(secondsetselection.content) - 1]
            else:
                await ctx.send(">>> Invalid number")
                return
        else:
            if secondsetselection.content.title() in gearset2:
                setselection2 = secondsetselection.content.title()
            else:
                await ctx.send(">>> No set found")
                return

        if setselection2 == gearset2[8] or setselection2.lower() == "none":
            setselection2 = " "
            await ctx.send(">>> You have picked " + setselection4)
            finalsetselection = setselection4
        else:
            await ctx.send(">>> You have picked " + setselection4 + " + " + setselection2)
            finalsetselection = f"{setselection4} + {setselection2}"

    await ctx.send(">>> Upload a build image")

    def checkimage(message):
        attachments = message.attachments
        if len(attachments) == 0:
            return False
        attachment = attachments[0]
        return attachment.filename.endswith(('.jpg', '.png', 'jpeg'))

    try:
        msg = await client.wait_for('message', timeout=60.0, check=checkimage)
    except asyncio.TimeoutError:
        await ctx.send(f">>> I'm tired of waiting . . .")
        return

    try:
        image = msg.attachments[0].url
        await ctx.send('>>> loading . . .')
    except IndexError:
        print(">>> Error: No attachments")
        await ctx.send(">>> No image submitted")
    else:
        if image[0:26] == "https://cdn.discordapp.com":
            r = requests.get(image, stream=True)
            linename = unitselection.title() + ": " + finalsetselection
            tempimagename = unitselection.title() + ":" + finalsetselection + ".jpg"
            download_file("tempunitinfosets.txt", "/unit_and_imgurlinks.txt")
            with open("tempunitinfosets.txt") as file:
                for line in file:
                    if line.split(';')[0] == linename:
                        await ctx.send(">>> Unit already exists!")
                        return

            with open(tempimagename, 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)

            PATH = tempimagename
            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(PATH, title=str(linename))
            os.remove(tempimagename)
            download_file("tempfile.txt", "/unit_and_imgurlinks.txt")
            f = open("tempfile.txt", "a")
            f.write(linename + "; " + uploaded_image.link + "\n")
            print(uploaded_image.link)
            f.close()
            dbx.files_delete_v2("/unit_and_imgurlinks.txt")
            upload_file("/unit_and_imgurlinks.txt", "tempfile.txt")
            os.remove("tempfile.txt")
            os.remove("tempunitinfo.txt")
            await ctx.send(">>> Unit added! \nCheck with the command !unitbuilds")


     
@client.command()
async def unitbuilds(ctx, *args):
    names = []
    descriptions = []

    class_dict = {"Knight": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Knight.png",
                  "Warrior": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Warrior.png",
                  "Mage": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Mage.png",
                  "Ranger": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Ranger.png",
                  "Thief": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Thief.png",
                  "Soul Weaver": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Soul%20Weaver.png",
                  }

    element_dict = {"Dark": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Dark.png",
                    "Light": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Light.png",
                    "Fire": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Fire.png",
                    "Ice": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Ice.png",
                    "Earth": "https://epic7x.com/wp-content/themes/epic7x/assets/img/Earth.png"}

    color_dictionary = {"Dark": discord.Color.dark_purple(),
                        "Light": discord.Color.from_rgb(234, 234, 9),
                        "Fire": discord.Color.from_rgb(238, 26, 15),
                        "Ice": discord.Color.from_rgb(79, 165, 255),
                        "Earth": discord.Color.from_rgb(6, 209, 8)}

    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author

    if not args:
        # asks user who, then lists out names
        await ctx.send(">>> Which unit would you like to look at? \n")

        download_file("tempfile.txt", "/unit_and_imgurlinks.txt")
        # adds units to names array
        with open("tempfile.txt") as file:
            for line in file:
                names.append(line.split(':')[0])

        # makes names unique
        my_set = list(set(names))

        # sorts set
        my_set = sorted(my_set)

        # prints out names in proper format
        listedoutnames = ""
        for i in range(len(my_set)):
            listedoutnames += (str(i + 1) + " : " + str(my_set[i]) + "\n")
        await ctx.send(f"```{listedoutnames}```")

        # user input unit name or number
        unit = await client.wait_for("message", check=check)

        if unit.content.isdigit():
            if int(unit.content) <= len(my_set) and int(unit.content) != 0:
                userinputtedunit = my_set[int(unit.content) - 1].lower()
            else:
                await ctx.send(">>> Invalid choice")
                return
        else:
            userinputtedunit = str(unit.content).lower()

        # scans text file
        with open("tempfile.txt") as file:
            for line in file:
                unitname = line.split(':')[0].lower()
                # if user input is in the text file
                if unitname.lower() == userinputtedunit:
                    # adds the unit set and link to the array
                    start = ': '
                    end = ';'
                    descriptions.append(
                        (line[line.find(start) + len(start):line.rfind(end)]) + " : " + line.split(';')[1].strip())

        stringofdescriptions = ""

        # turns all description into block of text
        for i in descriptions:
            stringofdescriptions += (str(i) + "\n")

        # changes all names in array to lower
        for i in range(len(names)):
            names[i] = names[i].lower()

        # checks if user input is in the names-array
        if unit.content.lower() not in names and not unit.content.isdigit():
            await ctx.send(">>> No unit found!")
            return
        # creates an embed
        else:
            embed = discord.Embed(
                # title=userinputtedunit.title(),
            )

            unitcolor = ""
            uniturl = ""
            download_file("tempunitinfo.txt", "/unit_info.txt")
            # scans unit-info and gets the unit-thumbnail-url and unit color
            with open("tempunitinfo.txt") as file:
                for line in file:
                    # if unit-info's name is same as user inputted name
                    if line.split(':')[0].lower() == userinputtedunit:
                        uniturl = line.split('|')[1].strip()
                        start_color = ': '
                        end_color = ';'
                        start_class = "; "
                        end_class = "|"
                        unitelement = (element_dict[
                            (line[line.find(start_color) + len(start_color):line.rfind(end_color)]).strip()])
                        unitcolor = (color_dictionary[
                            (line[line.find(start_color) + len(start_color):line.rfind(end_color)]).strip()])
                        unitclass = (
                            class_dict[(line[line.find(start_class) + len(start_class):line.rfind(end_class)]).strip()])
            # sets embed description, thumbnail, and color
            embed.set_author(name=userinputtedunit.upper(), icon_url=unitelement)
            embed.description = f" {stringofdescriptions}\n\n"
            embed.set_thumbnail(url=uniturl)
            embed.colour = unitcolor
            embed.set_footer(text=chr(173), icon_url=unitclass)
            await ctx.send(embed=embed)

            os.remove("tempfile.txt")
            os.remove("tempunitinfo.txt")


            
client.run(os.getenv('GENJI_TOKEN'))
