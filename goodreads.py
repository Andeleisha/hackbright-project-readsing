
import os
import xmltodict 
import requests
import re

##############################################################################

GR_DEV_KEY = os.environ["GOODREADS_DEV_KEY"]

##############################################################################

def search_goodreads(search_string):
    """Takes in a string and searches Goodreads API by title, author, and ISBN, returns a response object."""
    search_url = "https://www.goodreads.com/search/index.xml"

    search_params = {
        "q" : search_string, 
        "key" : GR_DEV_KEY
    }

    response = requests.get(url=search_url, params=search_params)

    return response

def parse_search_goodreads(search_response):
    """Takes the response object from Goodreads and returns a list of book objects."""

    if search_response.status_code != 200:
        print(search_response.status_code)
        search_results = "Error"
    else:
        response_dict = xmltodict.parse(search_response.content)
        search_results = response_dict["GoodreadsResponse"]["search"]["results"]["work"]

    return search_results

def search_for_book(user_search):
    """Searches Goodreads and returns a list of book objects"""

    response = search_goodreads(user_search)

    search_results = parse_search_goodreads(response)

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

    raw_book_description = book_info["description"]

    clean = re.compile('<.*?>')
    book_description = re.sub(clean, '', raw_book_description)

    return book_description