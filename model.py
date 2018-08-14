##############################################################################
from flask_sqlalchemy import SQLAlchemy


##############################################################################
db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of my site."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sp_username = db.Column(db.String(30), nullable=False)
    sp_access = db.Column(db.String(100), nullable=False)
    sp_refresh = db.Column(db.String(100), nullable=False)
    sp_expires = db.Column(db.String(100), nullable=False)
    gr_username = db.Column(db.String(30), nullable=True)
    gr_access = db.Column(db.String(100), nullable=True)
    gr_expires = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} sp_username={self.spo_username}>"

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