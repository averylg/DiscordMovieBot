import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()


def get_search_results(movie: str):
    """
    Searches the OMDb and returns a list of movies, series, and other results from the search.

    If no results are found, the function just returns an empty string.

    Parameters
    ----------
    movie : str
        The movie/show being searched for

    Returns
    -------
    list
        a list of search results (converted from JSON to dictionaries)
    """

    try:
        result = requests.get('http://www.omdbapi.com/?s=' + movie + '&apikey=' + os.getenv("API_KEY"))
        return json.loads(result.text)["Search"]
    except:
        return ""


def get_movie_from_results_by_id(movie_results, imdb_id):
    """
    Used to get a movie by ID from a movie_results map array
    :param movie_results:
    :param imdb_id:
    :return:
    """
    for movie in movie_results:
        if movie["imdbID"] == imdb_id:
            print(movie)
            return movie
    return False
