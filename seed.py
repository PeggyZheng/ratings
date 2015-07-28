"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app
import datetime

def load_users():
    """Load users from u.user into database."""
    users_file = open('./seed_data/u.user')
    for line in users_file:
        user_data = line.rstrip().split('|')
        # print "zipcode=", "*", user_data[4], "*"
        individual_user = User(user_id=user_data[0], age=user_data[1], zipcode=user_data[4])
        db.session.add(individual_user)
    db.session.commit()




def load_movies():
    """Load movies from u.item into database."""

    movies_file = open('./seed_data/u.item')
    for line in movies_file:
        movie_data = line.rstrip().split('|')
        movie_title = (" ").join(movie_data[1].split(" ")[:-1])
        if movie_data[2] != "":
            parsed_datetime = datetime.datetime.strptime(movie_data[2], '%d-%b-%Y')
            print parsed_datetime
            individual_movie = Movie(movie_id=movie_data[0], title=movie_title, released_at=parsed_datetime, imdb_url=movie_data[4])
        else:
            individual_movie = Movie(movie_id=movie_data[0], title=movie_title, imdb_url=movie_data[4])
        db.session.add(individual_movie)
    db.session.commit()



def load_ratings():
    """Load ratings from u.data into database."""
    ratings_file = open('./seed_data/u.data')
    for line in ratings_file:
        ratings_data = line.rstrip().split('\t')
    
        individual_rating = Rating(movie_id=ratings_data[1], user_id=ratings_data[0], score=ratings_data[2])

        db.session.add(individual_rating)
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_movies()
    load_ratings()
