import os
import yaml
import logging
import time
import json
import asyncio

import discord
from discord.ext import commands, tasks

import websockets

from dotenv import load_dotenv

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)

# Reading from a YAML file
with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)

host = settings['host']
port = settings['port']
server_ws_uri = f"ws://{host}:{port}/ws/discord_handler"

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD = int(os.getenv('DISCORD_GUILD_ID'))

intents = discord.Intents.all()
command_prefix = '/'
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
Lucid_channel_id = settings['discord']['channels']['Lucid_channel_id']
log_channel_id = settings['discord']['channels']['log_channel_id']
new_summary = "No summary has been generated yet."
async def send_discord_message(content, channel_id=Lucid_channel_id, guild_id=GUILD):
    print(f"Sending message to channel {channel_id} in guild {guild_id}.")
    guild = bot.get_guild(guild_id)
    if guild is None:
        print(f"Guild with ID {guild_id} not found.")
        return

    channel = guild.get_channel(channel_id)
    if channel is None:
        print(f"Channel with ID {channel_id} not found in guild {guild.name}.")
        return

    try:
        await channel.send(content)
        print("Message sent successfully.")
    except discord.HTTPException as e:
        print(f"Failed to send message: {e}")

class DiscordConnectionManager:
    def __init__(self):
        self.server_websocket = None

    async def connect_to_server(self):
        self.server_websocket = await websockets.connect(server_ws_uri)

    async def send_to_server(self, message):
        await self.server_websocket.send(json.dumps(message))

    async def receive_from_server(self):
        while True:
            data = await self.server_websocket.recv()
            data = json.loads(data)
            print("Received data from server:", data)
            message_type = data.get("type")
            content = data.get("content")
            match message_type:
                case "log":
                    await send_discord_message(content, channel_id=log_channel_id)
                case "Lucid_discord_message":
                    await send_discord_message(content, channel_id=Lucid_channel_id)
            # Process the received message as needed

discord_connection_manager = DiscordConnectionManager()

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
    
    print("Connecting to server...")
    
    await send_discord_message("```md\nLucid is now ONLINE.\n```", channel_id=log_channel_id)
    
    await discord_connection_manager.connect_to_server()

    asyncio.create_task(discord_connection_manager.receive_from_server())

@bot.event
async def on_message(message):
    if message.content[0] == "/":
        await bot.process_commands(message)
        return
    if message.channel.id == Lucid_channel_id:
        # This function will be called whenever a message is sent in the specified channel
        if message.author != bot.user:
            formatted_message = {'content': message.content, 'source': message.author.name, 'timestamp': time.time(), 'type': 'discord_user_message'}
            await discord_connection_manager.send_to_server(formatted_message)

@bot.command(name='summary')
async def get_summary(ctx):
    global new_summary
    await send_discord_message(f"```md\nSummary:\n{new_summary}\n```", channel_id=log_channel_id)

if __name__ == '__main__':
    bot.run(TOKEN)
