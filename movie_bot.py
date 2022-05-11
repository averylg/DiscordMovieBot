import os
from dotenv import load_dotenv
from bot import bot

from pymongo import MongoClient

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
MONGO = os.getenv("MONGO_URL")

client = MongoClient(MONGO)
db = client.movies

bot.run(TOKEN)

