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
    """login page for user"""
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
    """Log out the user; remove the user from the session and flash a notificatio message"""
    session.pop('loggedin', None)

    flash("You have logged out")
    return redirect(url_for('index'))
    

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    """show the details of the users, include its user id, age, zipcode and movies that they rate"""
    user = User.query.get(user_id)
    score_and_title = db.session.query(Movie.movie_id, Movie.title, Rating.score).join(Rating).filter(Rating.user_id==user_id).order_by(Movie.title).all()
    return render_template('user_profile.html', user=user, score_and_title=score_and_title)

@app.route('/movies/<int:movie_id>')
def show_movie_details(movie_id):
    """show the details of the movies that include the a dropdown menu that allows the users to 
    update/add their ratings and show the all the ratings for that specific movie"""
    movie = Movie.query.get(movie_id)
    ratings = movie.ratings



    user_id = session.get("loggedin")

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.
    print "user id is", user_id
    if user_id:
        user = User.query.get(user_id)
        print "user is", user
        if user:
            print "this is where we generate prediction"
            prediction = user.predict_rating(movie)
    print "This is a test to see prediction", prediction

    return render_template(
        "movie_profile.html",
        movie=movie,
        user_rating=user_rating,
        average=avg_rating,
        prediction=prediction,
        ratings=ratings
        )


@app.route('/movies/<int:movie_id>', methods=['POST'])
def update_movie_rating(movie_id):
    """update the ratings for a particular movie and particular users and update the db"""
    score = int(request.form.get('score'))
    if session.get('loggedin', None):
        user_id = session['loggedin']
        has_rated = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
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