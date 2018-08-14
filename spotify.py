
import os
import json
import requests

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