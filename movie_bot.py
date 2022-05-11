import os
from dotenv import load_dotenv
from bot import bot

from pymongo import MongoClient

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
MONGO_PW = os.getenv("MONGO_PW")
mcl = ''
if MONGO_PW == 'testing':
    mcl = 'localhost'
else:
    mcl = f"mongodb+srv://dipchest:{MONGO_PW}@greg.hrim0.mongodb.net/Greg?retryWrites=true&w=majority"
client = MongoClient(mcl)
db = client.movies

print(client.list_database_names())

bot.run(TOKEN)

