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

