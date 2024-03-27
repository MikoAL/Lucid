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
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD = os.getenv('DISCORD_GUILD_ID')

intents = discord.Intents.all()
 
bot = commands.Bot(command_prefix='!', intents=intents)
Lucid_channel_id = int("1222433056778879016")

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
    
@bot.event
async def on_message(message):
    if message.channel.id == Lucid_channel_id:
        # This function will be called whenever a message is sent in the specified channel
        if message.author != bot.user:
            await process_message(message)
            
async def process_message(message):
    # Your custom processing logic for the message goes here
    # For example, you can print the content of the message
    print(message)
    print(f"{message.author.name}: {message.content}")
    await send_message("I received your message: " + message.content, message.channel.id)
"""
For the bot to collect all the messages sent in a channel.


"""
async def send_message(message, channel_id=Lucid_channel_id):
    await bot.get_channel(channel_id).send(message)

if __name__ == '__main__':
    bot.run(TOKEN)
    