import discord
from discord.ext import commands
from search import get_search_results
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO = os.getenv("MONGO_URL")

client = MongoClient(MONGO)
db = client.movies

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

results = []

listmessage = []

vote_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']


@bot.event
async def on_ready():
    print('You are my superstar!')


@bot.command()
async def vent(ctx, *args):
    """Easter egg command"""
    if len(args) == 0 or args[0].lower() != 'gregory':
        await ctx.send('You need to vent. I know it will be hard for you to be sus but i know you can do it gregory')
    else:
        await ctx.send('Gregory, do you see the small vent on the floor? Have you ever heard of among us, gregory?')


@bot.command(name='search')
async def search_movies(ctx, *args):
    results.clear()
    if ctx.channel.name == 'movie-search':
        if len(args) == 0:
            await ctx.send("Format: `$search <movie or series being searched for>`")
        else:
            if get_search_results(' '.join(args)) == "":
                await ctx.send("No results available")
            else:
                for movie in get_search_results(' '.join(args)):
                    if movie["Type"] == "movie" or movie["Type"] == "series" and movie["Poster"] != "N/A":
                        year = movie["Year"]
                        if year.endswith("–"):
                            year = movie["Year"] + "Present"
                        e = discord.Embed()
                        e.set_image(url=movie["Poster"])
                        result = await ctx.send(
                            "{title} - {type} ({year})".format(title=movie["Title"], type=movie["Type"].capitalize(),
                                                               year=year), embed=e)

                        # await ctx.send(embed=e)
                        await result.add_reaction('⬆')
                        results.append(result)
    else:
        await ctx.send("Command must be sent in channel `movie-search`")


@bot.command(name='clear')
async def on_clear(ctx):
    for result in results:
        await result.delete()
    results.clear()


@bot.command(name='reset')
async def on_reset_command(ctx, *args):
    msg = await ctx.send(
        'Are you sure you want to reset the entire poll? React with 🇾 if yes, 🇳 if no, 🇻 to only clear votes')
    await msg.add_reaction('🇾')
    await msg.add_reaction('🇳')
    await msg.add_reaction('🇻')


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.count >= 2 and reaction.emoji == '⬆':
        if db.watchlist.find_one({'Title': reaction.message.content}) is None:
            result = db.watchlist.insert_one({
                'Title': reaction.message.content,
                'Votes': 0
            })

        else:
            reaction.message.channel.send("Movie already in database, movie board not changed.")
        if (len(results) != 0):
            for result in results:
                await result.delete()
        results.clear()
        movie_string = "**==MOVIE POLL==**\n**===========================**\n"
        counter = 1
        for item in db['watchlist'].find({}):
            movie_string += f"{counter}. {item['Title']} | **Votes: [{item['Votes']}]**\n"
            counter += 1
        await listmessage[0].edit(content=movie_string)
        await listmessage[0].add_reaction(vote_emojis[counter - 2])
    elif reaction.emoji in vote_emojis:
        ind = vote_emojis.index(reaction.emoji)
        movie_obj = db['watchlist'].find({})[ind]

        filter = {
            'Title': movie_obj['Title']
        }
        votes = {
            '$set': {
                'Votes': reaction.count - 1
            }
        }
        db['watchlist'].update_one(filter, votes)
        movie_string = "**==MOVIE POLL==**\n**===========================**\n"
        counter = 1
        for item in db['watchlist'].find({}):
            movie_string += f"{counter}. {item['Title']} | **Votes: [{item['Votes']}]**\n"
            counter += 1
        await reaction.message.edit(content=movie_string)


    elif reaction.count >= 2 and reaction.emoji == '🇳':
        await reaction.message.delete()
    elif reaction.count >= 2 and reaction.emoji == '🇾':
        await reaction.message.delete()
        db['watchlist'].delete_many({})
        if len(listmessage) != 0:
            await listmessage[0].delete()
            listmessage.clear()
        db['users'].update_many({}, {
            '$set': {
                'HasVoted': False,
                'MovieChosen': ''
            }
        })
    elif reaction.count >= 2 and reaction.emoji == '🇻':
        condition = {
            '$set': {
                'Votes': 0
            }
        }
        db['watchlist'].update_many({}, condition)
        movie_string = await _create_list_message()
        msg = await reaction.message.channel.send(movie_string)
        listmessage.append(msg)
        for i in vote_emojis:
            if vote_emojis.index(i) >= db['watchlist'].count_documents(filter={}):
                break
            await msg.add_reaction(i)
        await reaction.message.delete()
        db['users'].update_many({}, {
            '$set': {
                'HasVoted': False,
                'MovieChosen': ''
            }
        })


@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji in vote_emojis:
        ind = vote_emojis.index(reaction.emoji)
        movie_obj = db['watchlist'].find({})[ind]

        filter = {
            'Title': movie_obj['Title']
        }
        votes = {
            '$set': {
                'Votes': reaction.count - 1
            }
        }
        db['watchlist'].update_one(filter, votes)
        movie_string = "**==MOVIE POLL==**\n**===========================**\n"
        counter = 1
        for item in db['watchlist'].find({}):
            movie_string += f"{counter}. {item['Title']} | **Votes: [{item['Votes']}]**\n"
            counter += 1
        await reaction.message.edit(content=movie_string)


@bot.command(name='delete')
async def delete_movie(ctx, *args):
    if len(args) == 0:
        await ctx.send("Format this command as follows: $delete [index of movie in list]")
    else:
        movie_list = list(db['watchlist'].find())
        movie_to_delete = movie_list[int(args[0]) - 1]
        db['watchlist'].find_one_and_delete(movie_to_delete)

        movie_string = await _create_list_message()
        msg = await ctx.send(movie_string)
        listmessage.append(msg)
        for i in vote_emojis:
            if vote_emojis.index(i) >= db['watchlist'].count_documents(filter={}):
                break
            await msg.add_reaction(i)


@bot.command(name='list')
async def list_movies(ctx):
    if ctx.channel.name == 'watchlist':
        if db['watchlist'].find({}).count() == 0:
            await ctx.send("`The current watchlist is empty.`")
        movie_string = await _create_list_message()
        msg = await ctx.send(movie_string)
        listmessage.append(msg)
        for i in vote_emojis:
            if vote_emojis.index(i) >= db['watchlist'].count_documents(filter={}):
                break
            await msg.add_reaction(i)
    else:
        await ctx.send("This command can only be sent in the `watchlist` channel")


async def _create_list_message():
    if len(listmessage) != 0:
        await listmessage[0].delete()
        listmessage.clear()
    movie_string = "**==MOVIE POLL==**\n**===========================**\n"
    counter = 1
    for item in db['watchlist'].find({}):
        movie_string += f"{counter}. {item['Title']} | **Votes: [{item['Votes']}]**\n"
        counter += 1
    return movie_string


