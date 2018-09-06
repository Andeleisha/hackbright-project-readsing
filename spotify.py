
import os
import json
import requests
from requests_futures.sessions import FuturesSession
# from nlp import check_for_term_id
from model import Book, connect_to_db, db

##############################################################################

SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

##############################################################################

def master_search(terms_list):
    """Master search"""
    

    search_responses = async_search_terms(terms_list)

    all_playlists = parse_search_responses(terms_list, search_responses)

    sorted_playlists = rank_playlists(all_playlists)

    return sorted_playlists


def async_search_terms(terms_list):
    """Attempt at async requests with session."""
    sp_token_url = "https://accounts.spotify.com/api/token"

    sp_request_payload = {
        "grant_type": "client_credentials",
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    sp_request = requests.post(url=sp_token_url, data=sp_request_payload)

    sp_response_data = json.loads(sp_request.text)
    access_token = sp_response_data["access_token"]

    search_api_endpoint = "https://api.spotify.com/v1/search"

    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    s = FuturesSession()

    responses = []

    for term in terms_list:
        search_args = {
            "q" : term, 
            "type" : "playlist"
        }

        pending_request = s.get(url=search_api_endpoint, headers=authorization_header, params=search_args)
        responses.append(pending_request)

    return responses


def parse_search_responses(terms_list, search_responses):

    i = 0

    playlist_dicts = []


    for each_response in search_responses:
        list_of_playlists = parse_search_object(each_response)
        if list_of_playlists != []:
            transformed_playlists = transform_list_of_playlists(list_of_playlists)
            playlist_dicts = playlist_dicts + transformed_playlists
            i += 1
        else:
            i += 1

    return playlist_dicts

def parse_search_object(search_object):
    """Takes a response, turns it into JSON, returns only the search results."""

    present = search_object.result()

    clean = json.loads(present.text)

    list_of_playlists = clean["playlists"]["items"]

    return list_of_playlists

def transform_list_of_playlists(list_of_playlists):
    """Loops through a list and returns a list of dictionaries."""

    new_list = []
    i = 0

    for each_playlist in list_of_playlists:
        new_dict = transform_playlist_to_dict(each_playlist)
        new_list.append(new_dict)
        i += 1

    return new_list

def transform_playlist_to_dict(playlist_object):
    """Takes a single playlist object and returns a smaller dictionary."""
    new_dict = { "spotify_id" : playlist_object["id"], 
                    "name" : playlist_object["name"], 
                    "image" : clean_images(playlist_object), 
                    "creator" : playlist_object["owner"]["display_name"], 
                    "creator_id" : playlist_object["owner"]["id"],
                    "link" : playlist_object["external_urls"]["spotify"]
    }

    return new_dict


def clean_images(playlist_object):
    """Inserts a placeholder image if no image to display."""

    if playlist_object["images"] == []:
        playlist_object["images"] = "https://i.imgur.com/aGUOi4m.jpg"
    elif type(playlist_object["images"]) == str:
        playlist_object["images"] = playlist_object["images"]
    else:
        playlist_object["images"] = playlist_object["images"][0]["url"]


    return playlist_object["images"]




def rank_playlists(list_of_playlists):
    """Takes in a list of dictionaries and returns a sorted list of unique dictionaries by count."""

    all_playlists_dict = {}

    all_playlists_count = {}

    for each_playlist in list_of_playlists:
        if each_playlist["spotify_id"] not in all_playlists_dict:
            all_playlists_dict[each_playlist["spotify_id"]] = each_playlist
        if each_playlist["spotify_id"] not in all_playlists_count:
            all_playlists_count[each_playlist["spotify_id"]] = 1
        else:
            all_playlists_count[each_playlist["spotify_id"]] += 1

    ids_sorted_playlists = sorted(((v, k) for (k, v) in all_playlists_count.items()), reverse=True)

    sorted_playlists = []

    for playlist in ids_sorted_playlists:
        playlist_id = playlist[1]
        sorted_playlists.append(all_playlists_dict[playlist_id])

    return sorted_playlists






























# Make requests, then write to DB all at once, use ordered lists to associate response objects wit each term

