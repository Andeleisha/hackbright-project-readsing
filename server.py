from flask import Flask, request, redirect, g, render_template
import requests
import os
import xmltodict
import json


##############################################################################
app = Flask(__name__)

GR_DEV_KEY = os.environ["GOODREADS_DEV_KEY"]

SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]

PROXEM_API_KEY = os.environ["PROXEM_API_KEY"]

##############################################################################


@app.route("/")
def homepage():
    # Landing page, main page to start searches from
    # Must log in to spotify to search (redirect to Spotify Login, then Spotify Callback)

    # Search for book title, author, etc
    # Dropdown from search bar shows results, user clicks to submit to /search
    return render_template("homepage.html")

@app.route("/spotify-login")
def spotify_auth():
    # Spotify auth
    # Redirect to Callback
    pass

@app.route("/spotify-login/callback")
def spotify_callback():
    # Create app-side user account
    # Get access token etc
    # Store access token, refresh token etc in user account
    # Store user_id in the session

    # Redirect back to /, flash "logged in message"
    pass

@app.route("/spotify-logout")
def spotify_logout():
    # Remove user from session
    pass

@app.route("/my-music")
def my_music():
    # Check user_id in session
    # Get access token from DB
    # NTH: Show user's playlists
    # NTH: allow user to recommend playlists
    pass

@app.route("/interim-search", methods=["POST"])
def interim_search():
    # List of possible selections to choose from
    # TO DO: Error handling if not 200 response 
    raw_user_search = request.form["booksearch"]

    search_url = "https://www.goodreads.com/search/index.xml"

    search_params = {
        "q" : raw_user_search, 
        "key" : GR_DEV_KEY
    }

    response = requests.get(url=search_url, params=search_params)

    response_dict = xmltodict.parse(response.content)

    search_results = response_dict["GoodreadsResponse"]["search"]["results"]["work"]

    return render_template("interim-search.html", search_results=search_results)

@app.route("/search", methods=["POST"])
def search():
    # Get book ID from search form submit
    # Get book description from GoodReads
    # Transform description into string
    # Send description to NLP, get response words back
    # (Am I getting sentiment, or just key phrases? If sentiment, evaluate for usability)
    # For loop: for each key phrase/sentiment/boook title/author, search spotify
    # Rank playlists
    # Return render playlists
    # TO DO: Error handling
    # TO DO: Clean book description
    
    book_id = request.form["bookselect"]

    search_url = "https://www.goodreads.com/book/show/"

    search_params = {
        "format" : "xml", 
        "key" : GR_DEV_KEY, 
        "id" : book_id 
    }

    response = requests.get(url=search_url, params=search_params)

    response_dict = xmltodict.parse(response.content)

    book_info = response_dict["GoodreadsResponse"]["book"]

    book_description = book_info["description"]

    nlp_url = "https://proxem-term-extraction-v1.p.mashape.com/api/TermExtraction/Extract?method=0&nbtopterms=20"
    
    nlp_params = {
        "X-Mashape-Key": PROXEM_API_KEY,
        "Accept": "applications/json",
        "Content-Type": "text/plain",


    }
   
    nlp_response = requests.post(url=nlp_url, headers=nlp_params, data=book_description)

    terms_dict = json.loads(nlp_response.content)

    terms_list = []

    for each_term in terms_dict["terms"]:
        terms_list.append(each_term["term"])

    # test_terms = ['wizarding', 'lord voldemort', 'harry', 'hogwarts', 'tells him the truth about', 'wildly imaginative', 'relatives', 'evil', 'wizarding world', 'high-stakes', 'an unforgettable', 'life', 'wizardry', 'magical powers', 'assembles', 'heartless', 'bottling', 'vanish', 'feels like']

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

    return render_template("search.html", book=book_info, sorted_playlists=sorted_playlists)

@app.route("/goodreads-login")
def goodreads_login():
    # Login with goodreads
    pass

@app.route("/goodreads-login/callback")
def goodreads_callback():
    # Store access token
    # Redirect to /mybooks
    pass
    
@app.route("/goodreads-logout")
def goodreads_logout():
    # Remove user_id from session
    pass

@app.route("/my-books")
def my_books():
    # Get access token from DB
    # Show shelves
    pass

if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")