
import os
import requests
import json
from model import Book, connect_to_db, db

##############################################################################

PROXEM_API_KEY = os.environ["PROXEM_API_KEY"]

##############################################################################


def search_key_terms_string(book_description):
    """Takes in a string and returns a list of key terms."""

    nlp_url = "https://proxem-term-extraction-v1.p.mashape.com/api/TermExtraction/Extract?method=0&nbtopterms=20"
    
    nlp_params = {
        "X-Mashape-Key": PROXEM_API_KEY,
        "Accept": "applications/json",
        "Content-Type": "text/plain",
        "nbtopterms" : 10,


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



    return terms_list



