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


@app.route('/login', methods=['POST'])
def login_user():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        flash("Logged in")
        session['loggedin'] = user.user_id
    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("New user has been added to database")
        session['loggedin'] = new_user.user_id
    print "test", session
    return redirect(url_for('index'))

@app.route('/logout')
def logout_user():
    session.pop('loggedin', None)
    flash("You have logged out")
    return redirect(url_for('index'))
    

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    print "line 58"
    user = User.query.get(user_id)
    print user
    user_age = user.age
    user_zipcode = user.zipcode
    movie_score = db.session.query(User.user_id, Rating.score, Movie.title).join(Rating).join(Movie).filter(User.user_id==user_id)
    print movie_score
    movie_list = []
    for user,rating, movie in movie_score.all():
        movie_list.append((movie, rating))
    return render_template('user_profile.html', user_id=user_id, user_age=user_age,\
        user_zipcode=user_zipcode, movie_list=movie_list)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()