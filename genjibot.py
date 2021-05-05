import discord
import os
from dotenv import load_dotenv
import grabd
from discord.ext import commands
import pyimgur
import requests
import shutil

# Load environment variables
load_dotenv()

#Connect to discord client
client = discord.Client()

async def run_calc():
    return grabd.run()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!gear'):
        channel = message.channel
        await message.channel.send (
                "Do you need to change the defaults?\nThe defaults are 85, purple, +15\n(y/n)"
        )
        def check(m):
            return (m.content == 'y' or m.content == 'n') and m.channel == channel

        msg = await client.wait_for('message', check=check)
        if msg.content == 'y':
            await channel.send(f"Please enter the gear lvl, gear type/color, and gear enhance lvl")

        await channel.send("Please enter the stats you wish to calculate, seperate by a space")

        arglist = ['atk', 'def', 'hp', 'spd']
        def check2(m):
            response_list = set(m.content.split(' '))
            print(response_list)
            return len(response_list) == 4 and m.channel == channel and set(response_list).issubset(set(arglist))
        msg = await client.wait_for('message', check=check2)
        await channel.send(f"Stats received: {msg.content}")

        await channel.send(f"Please enter the corresponding values for the stats above: {msg.content}")

        def check3(m):
            return m.channel == channel and len(m.content.split(' ')) == 4
        msg2 = await client.wait_for('message', check=check3)
        stats_list = zip(msg.content.split(' '), msg2.content.split(' '))

        stats_list = dict(stats_list)
        await channel.send("The stats received were:")
        for k, v in stats_list.items():
            await channel.send(f"{k, v}")

        await channel.send("**Calculating...** ")
        text = await run_calc()
        await channel.send(text)


        # if msg == 'y':
        #     await channel.send("Please enter the values to change!")
        # else:
        #     await channel.send("Please enter the four stats to calculate")





#Run the discord client
client.run(os.getenv('GENJI_TOKEN'))

