from flask import Flask, request, redirect, g, render_template
import goodreads
import nlp
import spotify
from model import Book, Keyword, Playlist, BookKeyword, PlaylistKeyword, connect_to_db


##############################################################################
app = Flask(__name__)

##############################################################################


@app.route("/")
def homepage():
    # TO DO Dropdown from search bar shows results, user clicks to submit to /search
    return render_template("homepage.html")

@app.route("/interim-search", methods=["POST"])
def interim_search():
    # TO DO: Error handling if not 200 response 
    raw_user_search = request.form["booksearch"]

    search_results = goodreads.search_for_book(raw_user_search)

    if search_results == "Error":
        return render_template("error.html")
    else:
        return render_template("interim-search.html", search_results=search_results)

@app.route("/search", methods=["POST"])
def search():
    # TO DO: Error handling
    # TO DO: Clean book description

    book_id = request.form["bookselect"]

    book_info = goodreads.get_book_by_id(book_id)

    book_description = goodreads.clean_book_description(book_info)

    terms_list = nlp.get_key_terms(book_description) 

    sorted_playlists = spotify.get_sorted_playlists(terms_list)

    return render_template("search.html", book=book_info, sorted_playlists=sorted_playlists, book_description=book_description)

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

if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, port=8080, host="0.0.0.0")
    