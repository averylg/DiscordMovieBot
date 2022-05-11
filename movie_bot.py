import os
from dotenv import load_dotenv
from bot import bot

from pymongo import MongoClient

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
MONGO_PW = os.getenv("MONGO_PW")

client = MongoClient(f"mongodb+srv://dipchest:{MONGO_PW}@greg.hrim0.mongodb.net/Greg?retryWrites=true&w=majority")
db = client.movies

bot.run(TOKEN)

