"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app
import datetime

def load_users():
    """Load users from u.user into database."""
    users_file = open('./seed_data/u.user')
    for line in users_file:
        user_data = line.split('|')
        individual_user = User(user_id=user_data[0], age=user_data[1], zipcode=user_data[4])
        db.session.add(individual_user)
        db.session.commit()




def load_movies():
    """Load movies from u.item into database."""

    movies_file = open('./seed_data/u.item')
    for line in movies_file:
        movie_data = line.split('|')
        parsed_datetime = datetime.datetime.strptime(movie_data[2], %d-%m-%Y)
        individual_movie = Movie(movie_id=movie_data[0], title=movie_data[1], released_at=movie_data[2], imdb_url=movie_data[4])
        db.session.add(individual_movie)
        db.session.commit()



def load_ratings():
    """Load ratings from u.data into database."""


if __name__ == "__main__":
    connect_to_db(app)

    # load_users()
    load_movies()
    load_ratings()
