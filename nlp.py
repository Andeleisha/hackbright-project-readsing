
import os
import requests
import json
from goodreads import clean_book_description

##############################################################################

PROXEM_API_KEY = os.environ["PROXEM_API_KEY"]

##############################################################################


def get_key_terms(book_description):
    """Takes in a book dictionary and returns a list of key terms."""

    # book_description = clean_book_description(book_info)

    nlp_url = "https://proxem-term-extraction-v1.p.mashape.com/api/TermExtraction/Extract?method=0&nbtopterms=20"
    
    nlp_params = {
        "X-Mashape-Key": PROXEM_API_KEY,
        "Accept": "applications/json",
        "Content-Type": "text/plain",


    }
   
    nlp_response = requests.post(url=nlp_url, headers=nlp_params, data=book_description.encode('utf-8'))

    terms_dict = json.loads(nlp_response.content)

    terms_list = []

    for each_term in terms_dict["terms"]:
        terms_list.append(each_term["term"])

    return terms_list