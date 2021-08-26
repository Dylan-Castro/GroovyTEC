import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import youtube_dl

load_dotenv()

# Get the API token from the .env file.
DISCORD_TOKEN = os.environ['discord_token']

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)