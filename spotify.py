
import os
import json
import requests
import grequests
from nlp import check_for_term_id
from model import Book, Keyword, Playlist, BookKeyword, PlaylistKeyword, connect_to_db, db

##############################################################################

SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

##############################################################################

def get_sorted_playlists(terms_list):
    """Takes in a list of terms, searches each term on spotify, compares results."""
    sp_token_url = "https://accounts.spotify.com/api/token"

    sp_request_payload = {
        "grant_type": "client_credentials",
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    sp_request = requests.post(url=sp_token_url, data=sp_request_payload)

    sp_response_data = json.loads(sp_request.text)
    access_token = sp_response_data["access_token"]
    token_type = sp_response_data["token_type"]
    expires_in = sp_response_data["expires_in"]

    search_api_endpoint = "https://api.spotify.com/v1/search"

    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    all_playlists_count = {}

    all_playlists_dict = {}

    for a_term in terms_list:
        search_args = {
            "q" : a_term, 
            "type" : "playlist"
        }

        key_term_playlists_request = requests.get(url=search_api_endpoint, headers=authorization_header, params=search_args)
        key_term_playlists = json.loads(key_term_playlists_request.text)


        
        for each_playlist in key_term_playlists["playlists"]["items"]:
            if each_playlist["id"] not in all_playlists_dict:
                all_playlists_dict[each_playlist["id"]] = each_playlist

            if each_playlist["id"] not in all_playlists_count:
                all_playlists_count[each_playlist["id"]] = 1
            else:
                all_playlists_count[each_playlist["id"]] += 1

    ids_sorted_playlists = sorted(((v, k) for (k, v) in all_playlists_count.items()), reverse=True)

    sorted_playlists = []

    for playlist in ids_sorted_playlists:
        playlist_id = playlist[1]
        sorted_playlists.append(all_playlists_dict[playlist_id])

    return sorted_playlists

####################################################################################

def check_for_playlists(terms_list):
    """Check if terms exist, returns list of playlists if true, searches if false, writes new lists and assoc to db."""
    # Check if term exists in PlaylistKeyword
    # Return list of playlists if true
    # Search term and return list of playlist if false
    # Write new term/playlists to dbs

    new_playlists = search_all_terms_for_playlists(terms_list)
    list_of_playlists = parse_list_search_objects(new_playlists)
    clean_list_of_playlists = transform_list_of_playlists(list_of_playlists)

    pass 

def check_term_for_playlists(term):
    """Checks if any playlists are associated with a given term."""
    keyword_id = check_for_term_id(term)
    query = PlaylistKeyword.query.filter_by(keyword_id=keyword_id).all()

    return query

def search_term_for_playlists(term):
    """Searches a term on spotify, returns a list of playlists."""
    sp_token_url = "https://accounts.spotify.com/api/token"

    sp_request_payload = {
        "grant_type": "client_credentials",
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    sp_request = requests.post(url=sp_token_url, data=sp_request_payload)

    sp_response_data = json.loads(sp_request.text)
    access_token = sp_response_data["access_token"]
    # token_type = sp_response_data["token_type"]
    # expires_in = sp_response_data["expires_in"]

    search_api_endpoint = "https://api.spotify.com/v1/search"

    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    search_args = {
        "q" : term, 
        "type" : "playlist"
    }

    response = requests.get(url=search_api_endpoint, headers=authorization_header, params=search_args)

    return response

def build_search_request(term):
    """Searches a term on spotify, returns a list of playlists."""
    sp_token_url = "https://accounts.spotify.com/api/token"

    sp_request_payload = {
        "grant_type": "client_credentials",
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    sp_request = requests.post(url=sp_token_url, data=sp_request_payload)

    sp_response_data = json.loads(sp_request.text)
    access_token = sp_response_data["access_token"]
    # token_type = sp_response_data["token_type"]
    # expires_in = sp_response_data["expires_in"]

    search_api_endpoint = "https://api.spotify.com/v1/search"

    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    search_args = {
        "q" : term, 
        "type" : "playlist"
    }

    pending_request = grequests.get(url=search_api_endpoint, headers=authorization_header, params=search_args)

    return pending_request

def make_async_search_requests(terms_list):
    """Loops through terms to search on spotify, returns a list of objects."""

    search_requests = []

    for each_term in terms_list:
        pending_request = build_search_request(each_term)
        search_requests.append(pending_request)

    responses = grequests.map(search_requests)

    return responses

def search_all_terms_for_playlists(terms_list):
    """Loops through terms to search on spotify, returns a list of objects."""

    all_playlists = []

    for each_term in terms_list:
        response = search_term_for_playlists(each_term)
        all_playlists.append(response)

    return all_playlists

def parse_search_object(search_object):
    """Takes a response, turns it into JSON, returns only the search results."""

    clean = json.loads(search_object.text)

    list_of_playlists = clean["playlists"]["items"]

    return list_of_playlists

def parse_list_search_objects(list_of_objects):
    """Parses multiple response objects."""

    all_playlists = []

    for item in list_of_objects:
        a_list = parse_search_object(item)
        all_playlists = all_playlists + a_list

    return all_playlists

def transform_playlist_to_dict(playlist_object):
    """Takes a single playlist object and returns a smaller dictionary."""
    new_dict = { "spotify_id" : playlist_object["id"], 
                    "name" : playlist_object["name"], 
                    "image" : playlist_object["images"][0]["url"], 
                    "creator" : playlist_object["owner"]["display_name"], 
                    "creator_id" : playlist_object["owner"]["id"],
                    "link" : playlist_object["external_urls"]["spotify"]
    }

    return new_dict

def transform_list_of_playlists(list_of_playlists):
    """Loops through a list and returns a list of dictionaries."""

    new_list = []

    for each_playlist in list_of_playlists:
        new_dict = transform_playlist_to_dict(each_playlist)
        new_list.append(new_dict)

    return new_list

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

def add_playlist_to_db(playlist_object):
    """Takes a playlist object and adds it to the DB."""
    spotify_id = playlist_object["id"]
    name = playlist_object["name"]
    image = playlist_object["images"][0]["url"]
    creator = playlist_object["owner"]["display_name"]
    creator_id = playlist_object["owner"]["id"]
    link = playlist_object["external_urls"]["spotify"]

    new_playlist = Playlist(spotify_id=spotify_id, name=name, image=image, creator=creator, creator_id=creator_id, link=link)

    db.session.add(new_playlist)
    db.session.commit()

def check_playlist_id(spotify_id):
    """Get playlist id by spotify id."""

    query = Playlist.query.filter_by(spotify_id=spotify_id).first()

    playlist_id = query.playlist_id

    return playlist_id

def add_playlist_term_to_db(term, spotify_id):
    """Add playlist and term to db."""

    playlist_id = check_playlist_id(spotify_id)

    keyword_id = check_for_term_id(term)

    new_playlist_keyword = PlaylistKeyword(playlist_id=playlist_id, keyword_id=keyword_id)

    db.session.add(new_playlist_keyword)
    db.session.commit()




# Make requests, then write to DB all at once, use ordered lists to associate response objects wit each term

