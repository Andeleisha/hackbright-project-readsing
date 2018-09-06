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
    last_searched = db.Column(db.DateTime)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Book 
                    book_id={self.book_id} 
                    gr_id={self.gr_id} 
                    name={self.name} 
                    author={self.author} 
                    description={self.description} 
                    image={self.image} 
                    sm_image={self.sm_image}
                    last_searched={self.last_searched}>"""



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