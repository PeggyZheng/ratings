"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, redirect, request, flash, session, url_for
from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/movies")
def movie_list():
    """Show list of movies."""
    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route('/login', methods=['POST'])
def login_user():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        flash("Logged in")
        session['loggedin'] = user.user_id
        return redirect(url_for('show_user_details', user_id=user.user_id))
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("New user has been added to database")
        session['loggedin'] = new_user.user_id
        return redirect(url_for('show_user_details', user_id=new_user.user_id))

@app.route('/logout')
def logout_user():
    session.pop('loggedin', None)

    flash("You have logged out")
    return redirect(url_for('index'))
    

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    user = User.query.get(user_id)
    score_and_title = db.session.query(Movie.title, Rating.score).join(Rating).filter(Rating.user_id==user_id).all()

    return render_template('user_profile.html', user=user, score_and_title=score_and_title)

@app.route('/movies/<int:movie_id>')
def show_movie_details(movie_id):
    movie = Movie.query.get(movie_id)
    ratings = movie.ratings

    return render_template('movie_profile.html', movie=movie, ratings=ratings)

@app.route('/movies/<int:movie_id>/update-rating', methods=['POST'])
def update_movie_rating(movie_id):

    score = int(request.form.get('score'))
    if session.get('loggedin', None):
        user_id = session['loggedin']
        has_rated = Rating.query.filter_by(user_id=user_id).first()
        if has_rated:
            has_rated.score = score
        else:
            movie_rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
            db.session.add(movie_rating)

        db.session.commit()
        flash('Your rating has been added/updated')

        return redirect(url_for('show_movie_details', movie_id=movie_id))
    else:
        flash('You need to login first')
        return redirect(url_for('index'))



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()