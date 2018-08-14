
import os
import xmltodict 
import requests

##############################################################################

GR_DEV_KEY = os.environ["GOODREADS_DEV_KEY"]

##############################################################################


def search_for_book(user_search):
    """Takes in a string and searches Goodreads API by title, author, and ISBN."""

    search_url = "https://www.goodreads.com/search/index.xml"

    search_params = {
        "q" : user_search, 
        "key" : GR_DEV_KEY
    }

    response = requests.get(url=search_url, params=search_params)

    response_dict = xmltodict.parse(response.content)

    search_results = response_dict["GoodreadsResponse"]["search"]["results"]["work"]

    return search_results

def search_book_by_id(book_id):
    """Takes in an integer and gets the book with that Goodreads ID."""
    search_url = "https://www.goodreads.com/book/show/"

    search_params = {
        "format" : "xml", 
        "key" : GR_DEV_KEY, 
        "id" : book_id 
    }

    response = requests.get(url=search_url, params=search_params)

    response_dict = xmltodict.parse(response.content)

    book_info = response_dict["GoodreadsResponse"]["book"]

    return book_info

def clean_book_description(book_info):
    """Takes in a book dictionary and returns a clean book description."""

    book_description = book_info["description"]

    return book_description