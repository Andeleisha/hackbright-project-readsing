
import os
import json
import requests
from requests_futures.sessions import FuturesSession
from nlp import check_for_term_id
from model import Book, Keyword, Playlist, BookKeyword, PlaylistKeyword, connect_to_db, db

##############################################################################

SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

##############################################################################

def master_search(terms_list):
    """Master search"""
    

    raw_existing_playlists = get_existing_playlists_from_list(terms_list)
    clean_existing_playlists = transform_list_db_playlist_to_dict(raw_existing_playlists)

    new_search_terms = check_terms_no_playlists(terms_list)

    # search_responses = search_all_terms_for_playlists(new_search_terms)
    search_responses = try_async_search(new_search_terms)

    new_playlists = parse_and_write(new_search_terms, search_responses)

    all_playlists = clean_existing_playlists + new_playlists

    sorted_playlists = rank_playlists(all_playlists)

    return sorted_playlists

def get_existing_playlists_from_list(terms_list):
    """Get the playlists for a list of terms."""
    
    existing_playlists = []

    for each_term in terms_list:
        keyword_id = check_for_term_id(each_term)
        term_pl_assoc = check_term_for_playlists(each_term)
        if term_pl_assoc != None:
            for each_assoc in term_pl_assoc:
                playlist_id = each_assoc.playlist_id
                playlist = get_playlists_by_id(playlist_id)
                existing_playlists += playlist

    return existing_playlists

def check_term_for_playlists(term):
    """Checks if any playlists are associated with a given term."""
    keyword_id = check_for_term_id(term)
    query = PlaylistKeyword.query.filter_by(keyword_id=keyword_id).all()

    return query

def get_playlists_by_id(playlist_id):
    """Get list of playlist objects by id."""
    query = Playlist.query.filter_by(playlist_id=playlist_id).all()

    return query


def transform_list_db_playlist_to_dict(list_of_playlist_objects):
    """Transforms a list."""
    playlists = []

    for each_playlist in list_of_playlist_objects:
        playlists.append(transform_db_playlist_to_dict(each_playlist))

    return playlists


def transform_db_playlist_to_dict(playlist_object):
    """Transform's a DB object into a dictionary."""
    
    new_dict = { "playlist_id" : playlist_object.playlist_id, 
                    "spotify_id" : playlist_object.spotify_id, 
                    "name" : playlist_object.name, 
                    "image" : playlist_object.image, 
                    "creator" : playlist_object.creator, 
                    "creator_id" : playlist_object.creator_id, 
                    "link" : playlist_object.link

    }

    return new_dict

def check_terms_no_playlists(terms_list):
    """Checks a list for terms that have been associated with playlists, 
    returns a list of terms that have no associatons."""

    new_terms = []

    for each_term in terms_list:
        query = check_term_for_playlists(each_term)
        if query == []:
            new_terms.append(each_term)

    return new_terms

def search_all_terms_for_playlists(terms_list):
    """Loops through terms to search on spotify, returns a list of objects."""

    all_playlists = []

    for each_term in terms_list:
        response = search_term_for_playlists(each_term)
        all_playlists.append(response)

    return all_playlists


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

def parse_and_write(terms_list, search_responses):

    i = 0

    playlist_dicts = []


    for each_response in search_responses:
        list_of_playlists = parse_search_object(each_response)
        if list_of_playlists != []:
            transformed_playlists = transform_list_of_playlists(list_of_playlists)
            playlist_dicts = playlist_dicts + transformed_playlists
            # for each_playlist in list_of_playlists:
            #     add_playlist_to_db(each_playlist)
            #     spotify_id = each_playlist["id"]
            #     add_playlist_term_to_db(terms_list[i], spotify_id)
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

    # playlist_object["images"] = "https://i.imgur.com/aGUOi4m.jpg"

    return playlist_object["images"]


def add_playlist_to_db(playlist_object):
    """Takes a playlist object and adds it to the DB."""
    spotify_id = playlist_object["id"]
    name = playlist_object["name"]
    image = clean_images(playlist_object)
    creator = playlist_object["owner"]["display_name"]
    creator_id = playlist_object["owner"]["id"]
    link = playlist_object["external_urls"]["spotify"]

    new_playlist = Playlist(spotify_id=spotify_id, name=name, image=image, creator=creator, creator_id=creator_id, link=link)

    db.session.add(new_playlist)
    db.session.commit()


def add_playlist_term_to_db(term, spotify_id):
    """Add playlist and term to db."""

    playlist_id = check_playlist_id(spotify_id)

    keyword_id = check_for_term_id(term)

    new_playlist_keyword = PlaylistKeyword(playlist_id=playlist_id, keyword_id=keyword_id)

    db.session.add(new_playlist_keyword)
    db.session.commit()


def check_playlist_id(spotify_id):
    """Get playlist id by spotify id."""

    query = Playlist.query.filter_by(spotify_id=spotify_id).first()

    playlist_id = query.playlist_id

    return playlist_id


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
####################################################################################
"""Working on making parallel requests."""
 





# def build_search_request(term):
#     """Searches a term on spotify, returns a list of playlists."""
#     sp_token_url = "https://accounts.spotify.com/api/token"

#     sp_request_payload = {
#         "grant_type": "client_credentials",
#         'client_id': SPOTIFY_CLIENT_ID,
#         'client_secret': SPOTIFY_CLIENT_SECRET,
#     }

#     sp_request = requests.post(url=sp_token_url, data=sp_request_payload)

#     sp_response_data = json.loads(sp_request.text)
#     access_token = sp_response_data["access_token"]
#     # token_type = sp_response_data["token_type"]
#     # expires_in = sp_response_data["expires_in"]

#     search_api_endpoint = "https://api.spotify.com/v1/search"

#     authorization_header = {"Authorization": "Bearer {}".format(access_token)}

#     search_args = {
#         "q" : term, 
#         "type" : "playlist"
#     }

#     pending_request = grequests.get(url=search_api_endpoint, headers=authorization_header, params=search_args)

#     return pending_request

# def make_async_search_requests(terms_list):
#     """Loops through terms to search on spotify, returns a list of objects."""

#     search_requests = []

#     for each_term in terms_list:
#         pending_request = build_search_request(each_term)
#         search_requests.append(pending_request)

#     responses = grequests.map(search_requests)

#     return responses

def try_async_search(terms_list):
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
    # token_type = sp_response_data["token_type"]
    # expires_in = sp_response_data["expires_in"]

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





def parse_list_search_objects(list_of_objects):
    """Parses multiple response objects."""

    all_playlists = []

    for item in list_of_objects:
        a_list = parse_search_object(item)
        all_playlists = all_playlists + a_list

    return all_playlists


def add_list_playlists_to_db(list_of_playlist_objects):
    """Takes a list of playlist objects and adds them all to the DB."""
    for each_playlist in list_of_playlist_objects:
        add_playlist_to_db(each_playlist)


def add_lists_playlists_terms_to_db(terms_list, playlists):
    """Write playlists and term assoc to db."""
    pass
























# Make requests, then write to DB all at once, use ordered lists to associate response objects wit each term

