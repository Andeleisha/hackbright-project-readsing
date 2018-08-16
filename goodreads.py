
import os
import xmltodict 
import requests
import re
from model import Book, Keyword, Playlist, BookKeyword, PlaylistKeyword, connect_to_db, db

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

def transform_search_goodreads(search_response):
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

    search_results = transform_search_goodreads(response)

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

    return response

def transform_book_object(book_object):
    """Takes in the raw JSON response and returns a dictionary"""

    response_dict = xmltodict.parse(book_object.content)

    book_info = response_dict["GoodreadsResponse"]["book"]

    return book_info

def transform_multi_authors(book_object):
    """If a book has multiple authors, replace the list with the first author in the list."""

    book_info = book_object

    if type(book_info["authors"]["author"]) == list:
        book_info["authors"]["author"] = book_info["authors"]["author"][0]

    return book_info


def get_book_by_id(book_id):
    """Gets the book object and cleans it nicely."""

    raw_book = search_book_by_id(book_id)

    book_dict = transform_book_object(raw_book)

    clean_authors = transform_multi_authors(book_dict)

    clean_description = clean_book_description(clean_authors)

    return clean_description

def clean_book_description(book_info):
    """Takes in a book dictionary and returns a clean book description."""

    raw_book_description = book_info["description"]

    clean = re.compile('<.*?>')
    book_description = re.sub(clean, '', raw_book_description)

    book_info["description"] = book_description

    return book_info

def check_if_book(book_id):
    """Checks if the book has already been searched."""

    query = Book.query.filter_by(gr_id=book_id).first()

    if query == None:
        print("Book not found")
        # run_new_search(book_id)
    else:
        # get_book_info(book_id)
        print(query)

def add_new_book(book_info):
    """Adds a new book to the database."""

    gr_id = book_info["id"]
    name = book_info["title"]
    author = book_info["authors"]["author"]["name"]
    description = book_info["description"]
    image = book_info["image_url"]
    sm_image = book_info["small_image_url"]

    new_book = Book(gr_id=gr_id, name=name, author=author, description=description, image=image, sm_image=sm_image)

    db.session.add(new_book)
    db.session.commit()

def run_new_search(book_id):
    """Runs search for new book, nlp, playlist, writes to DB"""

    book_search = search_book_by_id(book_id)

    book_info = transform_book_object(book_search)


