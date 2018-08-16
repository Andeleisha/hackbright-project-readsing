##############################################################################
from flask_sqlalchemy import SQLAlchemy


##############################################################################
db = SQLAlchemy()


##############################################################################
# Model definitions

class Book(db.Model):
    """Books that have been searched."""

    __tablename__ = "books"

    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    gr_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    sm_image = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Book 
                    book_id={self.book_id} 
                    gr_id={self.gr_id} 
                    name={self.name} 
                    author={self.author} 
                    description={self.description} 
                    image={self.image} 
                    sm_image={self.sm_image}>"""

class Keyword(db.Model):
    """Keywords that have been used."""

    __tablename__ = "keywords"

    keyword_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    word = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Keyword keyword_id={self.keyword_id} word={self.word}>"

class Playlist(db.Model):
    """Playlists that have been searched."""

    __tablename__ = "playlists"

    playlist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    spotify_id = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    creator = db.Column(db.String(30), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Playlist 
                    playlist_id={self.playlist_id} 
                    spotify_id={self.spotify_id} 
                    name={self.name} 
                    creator={self.creator} 
                    image={self.image} 
                    link={self.link}>"""

class BookKeyword(db.Model):
    """Books associated with keywords."""

    __tablename__ = "bookkeywords"

    bk_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), index=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey("keywords.keyword_id"), index=True)

    book = db.relationship("Book",
                           backref=db.backref("bookkeywords", order_by=bk_id))

    keyword = db.relationship("Keyword",
                           backref=db.backref("bookkeywords", order_by=bk_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<BookKeyword bk_id={self.bk_id} book_id={self.book_id} keyword_id={self.keyword_id}>"


class PlaylistKeyword(db.Model):
    """Playlists associated with keywords."""

    __tablename__ = "playlistkeywords"

    pk_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.playlist_id"), nullable=False)
    keyword_id = db.Column(db.Integer, db.ForeignKey("keywords.keyword_id"), nullable=False)

    keyword = db.relationship("Keyword",
                           backref=db.backref("playlistkeywords", order_by=pk_id))

    playlist = db.relationship("Playlist",
                           backref=db.backref("playlistkeywords", order_by=pk_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<PlaylistKeyword pk_id={self.pk_id} playlist_id={self.playlist_id} keyword_id={self.keyword_id}>"


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///readsing'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)
    print("Connected to DB.")