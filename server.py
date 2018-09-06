from flask import Flask, request, redirect, g, render_template, jsonify, session
import goodreads
import nlp
import spotify
from model import Book, connect_to_db


##############################################################################
app = Flask(__name__)
app.secret_key = 'STUFFF'

##############################################################################


@app.route("/")
def homepage():
    # TO DO Dropdown from search bar shows results, user clicks to submit to /search
    return render_template("homepage.html")

@app.route("/interim-search", methods=["POST"])
def interim_search():
    # TO DO: Error handling if not 200 response 
    # print(request.form)
    # print(request.args)
    raw_user_search = request.form["booksearch"]

    try:
        search_results = goodreads.search_goodreads_for_book(raw_user_search)

    except:
        return render_template("error.html")

    
    return jsonify(search_results)

@app.route("/search")
def search():
    # TO DO: Error handling
    # TO DO: Clean book description
    
    book_id = session["book_id"]

    try:
        book_info = goodreads.check_for_book(book_id)

    except:
        return render_template("error.html")

    # terms_list = nlp.check_for_book_terms(book_info) 

    # sorted_playlists = spotify.master_search(terms_list)

    return render_template("search.html", book=book_info)

@app.route("/bookselect", methods=["POST"])
def bookselect():
    book_id = request.form.get("book_id")

    session["book_id"] = book_id

    return book_id

@app.route("/get-playlists", methods=["POST"])
def get_playlists():
    # In Jinja, import scripts to make AJAX work (jquery)
    # Also JS
    # Pass jinja variables in javascript: give them IDs in HTML
    # Make post call that will pass the description info to ajax route
    # Get the info on the AJAX route
    # Process as normal
    # JSONIFY sorted_playlists
    book_id = request.form.get("book_id")
    

    gr_id = request.form.get("gr_id")
    

    description = request.form.get("description")
    

    book_info = { "book_id" : book_id, 
                    "gr_id" : gr_id,
                    "description" : description}
    

    terms_list = nlp.search_new_terms(book_info)
    

    sorted_playlists = spotify.master_search(terms_list)
    
    

    return jsonify(sorted_playlists)

@app.route("/recent-books")
def recent_books():
    last_five_books = goodreads.get_recent_books()

    return jsonify(last_five_books)

@app.route("/about")
def about():

    return render_template("about.html")


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, port=8080, host="0.0.0.0")
    