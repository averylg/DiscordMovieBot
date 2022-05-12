import discord
from discord_components import Button, Select, SelectOption, ComponentsBot
from search import get_search_results, get_movie_from_results_by_id
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGO_PW = os.getenv("MONGO_PW")

mcl = ''
if MONGO_PW == 'testing':
    mcl = 'localhost'
else:
    mcl = f"mongodb+srv://dipchest:{MONGO_PW}@greg.hrim0.mongodb.net/Greg?retryWrites=true&w=majority"
client = MongoClient(mcl)
db = client.movies

intents = discord.Intents.default()
intents.members = True
# bot = commands.Bot(command_prefix='$', intents=intents)
cmd = '$'
if MONGO_PW == 'testing':
    cmd = '*'

bot = ComponentsBot(cmd)

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
    """$search <name of movie or series>"""
    results.clear()
    if ctx.channel.name == 'movie-search':
        if len(args) == 0:
            await ctx.send("Format: `$search <movie or series being searched for>`")
        else:
            options = []
            movie_results = get_search_results(' '.join(args))
            for movie in movie_results:
                if movie["Type"] == "movie" or movie["Type"] == "series" and movie["Poster"] != "N/A":
                    year = movie["Year"]
                    if year.endswith("–"):
                        year = movie["Year"] + "Present"
                    # e = discord.Embed()
                    # e.set_image(url=movie["Poster"])
                    # result = await ctx.send(
                    #     f"{movie['Title']} - {movie['Type'].capitalize()} ({year})", embed=e)
                    counter = 1
                    options.append(
                        SelectOption(
                            label=f"{movie['Title']} - {movie['Type'].capitalize()} ({year})",
                            value=movie["imdbID"]
                        ))
                    counter += 1
            if len(options) == 0:
                response = await ctx.send(
                    embed=discord.Embed(
                        color=discord.Color.from_rgb(0x2d, 0xe2, 0x6b),
                        description=f"No results for {' '.join(args)}"
                    ),
                    components=[
                        Button(label="No", style=4, custom_id="CloseSearch")
                    ]
                )
                x = True
                while x:
                    interaction = await bot.wait_for(
                        'button_click',
                        check=lambda i: i.custom_id == 'CloseSearch' and i.user == ctx.author
                    )
                    if interaction.custom_id == 'CloseSearch':
                        response.delete()
                        x = False
            else:
                options.append(SelectOption(label='❌ Cancel', value='cancel'))
                print(' '.join(args))
                response = await ctx.send(
                    embed=discord.Embed(
                        color=discord.Color.from_rgb(0x2d, 0xe2, 0x6b),
                        description=f"Results for {' '.join(args)}:"
                    ),
                    components=[
                        Select(
                            placeholder=f"Results for {' '.join(args)}",
                            options=options,
                            custom_id='SearchResults'
                        )
                    ]
                )
                a = True
                while a:
                    interaction = await bot.wait_for(
                        'select_option',
                        check=lambda inter: inter.custom_id == 'SearchResults' and inter.user == ctx.author
                    )
                    imdb_id = interaction.values[0]
                    if imdb_id == 'cancel':
                        await response.delete()
                        return
                    await response.delete()
                    movie_thing = get_movie_from_results_by_id(movie_results, imdb_id)

                    year = movie_thing["Year"]
                    if year.endswith("–"):
                        year = movie_thing["Year"] + "Present"
                    reee = discord.Embed(
                        color=discord.Color.from_rgb(0x2d, 0xe2, 0x6b),
                        title=f"{movie_thing['Title']} - {movie_thing['Type'].capitalize()} ({year})"

                    )
                    reee.set_image(url=movie_thing["Poster"])
                    response2 = await ctx.send(
                        embed=reee,
                        components=[
                            Button(label="Select", style=3, custom_id="ChooseMovie"),
                            Button(label="Go Back", style=4, custom_id="ChooseNope")
                        ]
                    )
                    b = True
                    while b:
                        interaction2 = await bot.wait_for(
                            'button_click',
                            check=lambda i: i.custom_id.startswith("Choose") # and i.user == ctx.author
                        )
                        if interaction2.user != ctx.author:
                            await ctx.send(f"Oi bud only {ctx.author} can click this right now here bud!")
                        print(interaction2.custom_id)
                        if interaction2.custom_id == 'ChooseMovie':
                            if db.watchlist.find_one({'Title': reee.title}) is None:
                                db.watchlist.insert_one({
                                    'Title': reee.title,
                                    'Votes': 0,
                                    'Voters': []
                                })
                                await response2.delete()
                            else:
                                await interaction2.send(
                                    embed=discord.Embed(
                                        color=discord.Color.from_rgb(0x2d, 0xe2, 0x6b),
                                        description="The item you selected is already in the watchlist."
                                    ),
                                    delete_after=10
                                )
                                await response2.delete()
                            b = False

                        elif interaction2.custom_id == 'ChooseNope':
                            await response2.delete()
                            await search_movies(ctx, *args)
                            b = False
                        a = False



    else:
        await ctx.send("Command must be sent in channel `movie-search`")


@bot.command(name='clear')
async def on_clear(ctx):
    """Clears the search results"""
    for result in results:
        await result.delete()
    results.clear()


@bot.command(name='reset')
async def on_reset_command(ctx, *args):
    """Prompt to either destroy the movie list or clear the vote counts"""
    msg = await ctx.send(
        content='Are you sure you want to reset the entire watchlist?',
        components=[
            Select(
                placeholder="Reset watchlist?",
                options=[
                    SelectOption(label='Yes', value='yes'),
                    SelectOption(label='No', value='no'),
                    SelectOption(label='Only clear vote counts', value='0'),
                ],
                custom_id='ResetWatchlist'
            )
        ],)
    interaction = await bot.wait_for('select_option', check=lambda inter: inter.custom_id == 'ResetWatchlist' and inter.user == ctx.author)
    res = interaction.values[0]

    if res == 'yes':
        await msg.delete()
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
    elif res == 'no':
        await msg.delete()
    elif res == '0':
        await msg.delete()
        condition = {
            '$set': {
                'Votes': 0
            }
        }
        db['watchlist'].update_many({}, condition)
        movie_string = await _create_list_message()
        movie_msg = await ctx.send(movie_string)
        listmessage.append(movie_msg)
        for i in vote_emojis:
            if vote_emojis.index(i) >= db['watchlist'].count_documents(filter={}):
                break
            await movie_msg.add_reaction(i)
        db['users'].update_many({}, {
            '$set': {
                'HasVoted': False,
                'MovieChosen': ''
            }
        })


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.count >= 2 and reaction.emoji == '⬆':
        if db.watchlist.find_one({'Title': reaction.message.content}) is None:
            result = db.watchlist.insert_one({
                'Title': reaction.message.content,
                'Votes': 0,
                'Voters': []
            })

        else:
            reaction.message.channel.send("Movie already in database, movie board not changed.")
        if len(results) != 0:
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
    """$delete <index in watchlist>"""
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


@bot.command(name='list', aliases=['watchlist', 'movielist', 'listmovies'])
async def watchlist(ctx):
    """Shows the user the list of movies and their vote counts"""
    e = discord.Embed(color=discord.Color.from_rgb(0x2d, 0xe2, 0x6b))
    e.title = "**Movie Watchlist**"
    movie_str = ''
    counter = 1
    options = []
    for item in db['watchlist'].find().sort('Votes', -1):
        movie_str += f"{counter}. {item['Title']} | Votes: [{item['Votes']}]\n"
        options.append(SelectOption(label=f"{counter}. {item['Title']}", value=str(item['_id'])))
        counter += 1
    e.description = movie_str
    msg = await ctx.send(
        embed=e,
        components=[
            Select(
                placeholder='Vote for something to watch!',
                options=options,
                custom_id='MovieVote'
            ),
            Button(
                label="Exit",
                style=4,
                custom_id="ExitList"
            )
        ]
    )
    c = True
    while c:
        interaction = await bot.wait_for(
            'select_option',
            check=lambda inter: (inter.custom_id == 'MovieVote' or inter.custom_id == 'ExitList') and inter.user == ctx.author
        )
        if interaction.custom_id == 'MovieVote':
            await msg.delete()
            c = False
        else:
            res = interaction.values[0]
            c = False
            filter1 = {
                '_id': ObjectId(res)
            }
            print(db.watchlist.find_one(filter1)['Voters'])
            if ctx.author.id in db.watchlist.find_one(filter1)['Voters']:
                await msg.delete()
                response = discord.Embed(color=discord.Color.from_rgb(0x2d, 0xe2, 0x6b))
                response.description = "You have already voted for this. Would you like to undo your vote?"
                msg2 = await ctx.send(
                    embed=response,
                    components=[
                        Button(label="Yes", style=3, custom_id="RemoveYes"),
                        Button(label="No", style=4, custom_id="RemoveNo")
                    ]
                )
                d = True
                while d:
                    interaction2 = await bot.wait_for('button_click', check=lambda i: i.custom_id.startswith("Remove") and i.user == ctx.author)
                    if interaction2.custom_id == 'RemoveYes':
                        votes = {
                            '$inc': {
                                'Votes': -1
                            },
                            '$pull': {
                                'Voters': ctx.author.id
                            }
                        }
                        db.watchlist.update_one(filter1, votes)
                        await msg2.delete()
                        await watchlist(ctx)
                    elif interaction2.custom_id == 'RemoveNo':
                        await msg2.delete()
                        await watchlist(ctx)
                    d = False
            else:
                votes = {
                    '$inc': {
                        'Votes': 1
                    },
                    '$push': {
                        'Voters': ctx.author.id
                    }
                }
                db.watchlist.update_one(filter1, votes)
                await msg.delete()
                await watchlist(ctx)


async def _create_list_message():
    if len(listmessage) != 0:
        await listmessage[0].delete()
        listmessage.clear()
    movie_string = "```\n==MOVIE POLL==\n===========================\n"
    counter = 1
    for item in db['watchlist'].find({}):
        movie_string += f"{counter}. {item['Title']} | Votes: [{item['Votes']}]\n"
        counter += 1
    return movie_string + "```"


