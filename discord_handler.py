# bot.py
import os
import yaml
import logging
import time
import json
from threading import Thread
import httpx

from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks


# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)

# Reading from a YAML file
with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)

host = settings['host']
port = settings['port']
server = f'http://{host}:{port}'


load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD = os.getenv('DISCORD_GUILD_ID')

intents = discord.Intents.all()
command_prefix = '/'
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
Lucid_channel_id = int("1222433056778879016")

client = httpx.AsyncClient()



new_summary = "No summary available."

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')
    get_message_from_server_loop.start()
    get_new_summary_loop.start()
    
@bot.event
async def on_message(message):
    if message.content[0] == "/":
        await bot.process_commands(message)
        return
    if message.channel.id == Lucid_channel_id:
        # This function will be called whenever a message is sent in the specified channel
        if message.author != bot.user:
            formatted_message = {'content':message.content,'source':message.author.name,'timestamp':time.time(), 'type':'discord_message'}
            async with bot.get_channel(Lucid_channel_id).typing():
                await send_user_message_to_server(formatted_message)

@bot.command(name='summary')
async def get_summary(ctx):
    global new_summary
    await ctx.send(f"```\nSummary:\n{new_summary}\n```")
"""
For the bot to collect all the messages sent in a channel.


"""
async def send_user_message_to_server(formatted_json: dict, server=server):
    print(f"Got message from {formatted_json['source']}: {formatted_json['content']}")
    await client.post(url=f'{server}/postbox', json=(formatted_json))

async def send_message_to_discord(message, channel_id=Lucid_channel_id):
    print(f"Sending message to channel")
    await bot.get_channel(channel_id).send(message)

async def get_message_from_server(server=server):
    server_response = ((await client.get(url=f'{server}/discord/fetch_newest_message')).json())
    
    #print(f"Server response: {server_response}")
    return server_response

async def get_summary_from_server(server=server):
    server_response = ((await client.get(url=f'{server}/discord/get_summary')).json())['content']
    return server_response

last_response = ""
@tasks.loop(seconds=0.1)
async def get_message_from_server_loop():
    global last_response
    #print("Getting response from server")
    try:
        response = await get_message_from_server()
        if response != last_response:
            print(f"Got response: {response}")
            last_response = response
            await send_message_to_discord(response)
    except Exception as e:
        print(f"Error: {e}")
        pass

@tasks.loop(seconds=0.1)
async def get_new_summary_loop():
    global new_summary
    try:
        response = await get_summary_from_server()
        if response != new_summary:
            print(f"Got summary: {response}")
            new_summary = response
    except Exception as e:
        print(f"Error: {e}")
        pass
if __name__ == '__main__':
    bot.run(TOKEN)
    