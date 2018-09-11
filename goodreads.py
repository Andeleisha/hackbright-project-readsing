
import os
import xmltodict 
import requests
import re
from model import Book, connect_to_db, db
import datetime

##############################################################################

GR_DEV_KEY = os.environ["GOODREADS_DEV_KEY"]


##############################################################################


def check_for_book(book_id):
    """Checks if the book has already been searched."""

    query = Book.query.filter_by(gr_id=book_id).first()

    if query == None:
        book_dict = get_goodreads_book_by_id(book_id)
        add_new_book(book_dict)
    else:
        book_dict = transform_book_db_obj_to_dict(query)
        update_or_add_book_db(book_dict)

    return book_dict



##############################################################################
"""Queries and helper functions used to search for books and display them in interim search"""

def search_goodreads(search_string):
    """Takes in a string and searches Goodreads API by title, author, and ISBN, returns a response object."""
    search_url = "https://www.goodreads.com/search/index.xml"

    search_params = {
        "q" : search_string, 
        "key" : GR_DEV_KEY
    }

    response = requests.get(url=search_url, params=search_params)

    if response.status_code != 200:
        print(response.status_code)
        raise Exception("Goodreads API not responding.")
    else:
        print("Success: returned search results from Goodreads")
        return response

def clean_response_search_goodreads(search_response):
    """Takes the response object from Goodreads and returns a list of book objects."""

    response_dict = xmltodict.parse(search_response.content)

    search_results = response_dict["GoodreadsResponse"]["search"]["results"]["work"]

    return search_results

def transform_search_goodreads_to_dict(book_object):
    """Turns the book object from a search into a dictionary with only the information used by the app."""

    book_dict = { "book_id" : "New",
                    "gr_id" : book_object["best_book"]["id"]["#text"], 
                    "name" : book_object["best_book"]["title"], 
                    "author" : book_object["best_book"]["author"]["name"],
                    "image" : book_object["best_book"]["image_url"],
                    "sm_image" : book_object["best_book"]["small_image_url"]
                    }

    return book_dict

def search_goodreads_for_book(user_search):
    """Searches Goodreads and returns a list of clean book objects"""

    response = search_goodreads(user_search)

    search_results = clean_response_search_goodreads(response)

    # new
    clean_results = []

    for each_book in search_results:
        clean_results.append(transform_search_goodreads_to_dict(each_book))

    return clean_results

##############################################################################
# Queries and Helper Functions for direct book queries

def search_goodreads_by_book_id(book_id):
    """Takes in an integer and searches Goodreads the book with that Goodreads ID."""
    search_url = "https://www.goodreads.com/book/show/"

    search_params = {
        "format" : "xml", 
        "key" : GR_DEV_KEY, 
        "id" : book_id 
    }

    response = requests.get(url=search_url, params=search_params)

    return response

def clean_book_object(book_object):
    """Takes in the raw JSON response and returns an uncleaned dictionary"""

    response_dict = xmltodict.parse(book_object.content)

    book_info = response_dict["GoodreadsResponse"]["book"]

    return book_info

def clean_multi_authors(book_object):
    """If a book has multiple authors, the author is equal to the first author in the list."""

    book_info = book_object

    if type(book_info["authors"]["author"]) == list:
        author = book_info["authors"]["author"][0]["name"]
    else:
        author = book_info["authors"]["author"]["name"]

    return author

def clean_book_description(book_object):
    """Takes in a book dictionary and returns a clean book description."""

    raw_book_description = book_object["description"]

    clean = re.compile('<.*?>')
    book_description = re.sub(clean, '', raw_book_description)

    return book_description

def transform_book_info_to_dict(book_object):
    """Turns the book object returned by a direct search into a dictionary with only the information used by the app."""

    book_dict = { "book_id" : "New",
                    "gr_id" : book_object["id"], 
                    "name" : book_object["title"], 
                    "author" : clean_multi_authors(book_object),
                    "description" : clean_book_description(book_object),
                    "image" : book_object["image_url"],
                    "sm_image" : book_object["small_image_url"]
                    }

    return book_dict



def get_goodreads_book_by_id(book_id):
    """Gets the book object and cleans it nicely."""

    raw_book = search_goodreads_by_book_id(book_id)

    book_info = clean_book_object(raw_book)

    book_dict = transform_book_info_to_dict(book_info)

    return book_dict

##############################################################################
# Queries and Helper Functions for database queries

def add_new_book(book_dict):
    """Adds a new book to the database."""

    gr_id = book_dict["gr_id"]
    name = book_dict["name"]
    author = book_dict["author"]
    description = book_dict["description"]
    image = book_dict["image"]
    sm_image = book_dict["sm_image"]
    last_searched = datetime.datetime.now()

    new_book = Book(gr_id=gr_id, name=name, author=author, description=description, image=image, sm_image=sm_image, last_searched=last_searched)

    db.session.add(new_book)
    db.session.commit()

def update_or_add_book_db(book_dict):
    """CHecks to see if the book already exists, if so, updates the timestamp, if not, adds it to DB."""
    query = Book.query.filter_by(gr_id=book_dict["gr_id"]).first()

    if query == None:
        add_new_book(book_dict)
    else:
        query.last_searched = datetime.datetime.now()
        db.session.commit()

def transform_book_db_obj_to_dict(book_object):
    """Turns the book object into a dictionary with only the information used by the app."""

    book_dict = { "book_id" : book_object.book_id,
                    "gr_id" : book_object.gr_id, 
                    "name" : book_object.name, 
                    "author" : book_object.author, 
                    "description" : book_object.description, 
                    "image" : book_object.image,
                    "sm_image" : book_object.sm_image 
                    }

    return book_dict

##############################################################################
"""Used to display recent searches on homepage"""


def get_recent_books():
    """Gets the five most recent books from the database."""

    query = Book.query.order_by("last_searched").all()

    last_five_books = []

    for book in query[-5:]:
        last_five_books.append(transform_book_db_obj_to_dict(book))

    return last_five_books

