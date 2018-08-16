
import os
import requests
import json
from model import Book, Keyword, Playlist, BookKeyword, PlaylistKeyword, connect_to_db, db

##############################################################################

PROXEM_API_KEY = os.environ["PROXEM_API_KEY"]

##############################################################################


def search_key_terms_string(book_description):
    """Takes in a string and returns a list of key terms."""

    # book_description = clean_book_description(book_info)

    nlp_url = "https://proxem-term-extraction-v1.p.mashape.com/api/TermExtraction/Extract?method=0&nbtopterms=20"
    
    nlp_params = {
        "X-Mashape-Key": PROXEM_API_KEY,
        "Accept": "applications/json",
        "Content-Type": "text/plain",


    }
   
    nlp_response = requests.post(url=nlp_url, headers=nlp_params, data=book_description.encode('utf-8'))

    return nlp_response

def search_key_terms_object(book_dict):
    """Takes in a book dictionary and returns a list of key terms."""

    book_description = book_dict["description"]

    response = search_key_terms_string(book_description)

    return response

def parse_key_terms(response):
    """Takes in a response object and returns a list of key terms."""

    terms_dict = json.loads(response.content)

    terms_list = []

    for each_term in terms_dict["terms"]:
        terms_list.append(each_term["term"])

    return terms_list
def search_new_terms(book_dict):
    """Takes a book dictionary, sends its description to NLP, returns list of key terms."""

    response = search_key_terms_object(book_dict)

    terms_list = parse_key_terms(response)

    add_new_terms_for_book(book_dict, terms_list)

    return terms_list

def check_for_term_id(term):
    """Check if terms are in DB."""
    query=Keyword.query.filter_by(word=term).first()

    if query == None:
        return None
    else:
        return query.keyword_id

def transform_terms_obj_to_dict(terms_obj):
    """Takes in a database object and returns a list of terms."""

def check_for_book_terms(book_dict):
    """Check if there are any terms associated with a book_id."""

    if book_dict["book_id"] != "New":
        query = BookKeyword.query.filter_by(book_id=book_dict["book_id"]).all()
        terms_list = "transformquery"
    else:
        terms_list = search_new_terms(book_dict)

    return terms_list

def add_new_term(term):
    """Adds a single new term to the DB."""
    new_term = Keyword(word=term)

    db.session.add(new_term)
    db.session.commit()

def add_new_term_for_book(book_id, term):
    """Ads a new term for a book."""

    new_term = BookKeyword(book_id=book_id, keyword_id=check_for_term_id(term))

    db.session.add(new_term)
    db.session.commit()

def add_new_terms_for_book(book_dict, terms_list):
    """Adds a list of terms to the DB."""
    query = Book.query.filter_by(gr_id=book_dict["gr_id"]).first()

    book_id = query.book_id

    for term in terms_list:
        add_new_term(term)
        add_new_term_for_book(book_id, term)

