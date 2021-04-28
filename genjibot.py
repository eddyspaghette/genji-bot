import discord
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

#Connect to discord client
client = discord.Client()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send (
                embed = discord.Embed(
                    title="Hello",
                    type="rich",
                    description="What am I doing?"
                )
        )



#Run the discord client
client.run(os.getenv('GENJI_TOKEN'))

