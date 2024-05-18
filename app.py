import requests
from flask import Flask, redirect, render_template, flash, request, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import SearchForm, UserAddForm, LoginForm
from models import db, connect_db, User, Favorites, Chapters

API_BASE_URL = "https://mangaverse-api.p.rapidapi.com/manga"
headers = {
	"X-RapidAPI-Key": "8f48217f34msh849af6055b461b3p1a4219jsna0ae0a9ba63a",
	"X-RapidAPI-Host": "mangaverse-api.p.rapidapi.com"
}

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mangareader'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)
app.app_context().push()
# db.drop_all()
# db.create_all()







@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]







@app.route('/users/favorite/<manga_title>', methods=['POST'])
def favorite_manga(manga_title):
    genre = request.args.get('genre')
    print('\n\n\nHERE\n\n\n')
    favorites = [like.name for like in g.user.favorites]
    if manga_title not in favorites:
        like = Favorites(user_id=g.user.id, name=manga_title)
        db.session.add(like)
        db.session.commit()
        return render_template('users/anime_picker.html', mangas=fetch_manga(genre), form=SearchForm())
    else:
        like = Favorites.query.filter(Favorites.user_id==g.user.id, Favorites.name==manga_title).first()
        db.session.delete(like)
        db.session.commit()
    print('\n\n\nHERE\n\n\n')
    return render_template('users/anime_picker.html', mangas=fetch_manga(genre), form=SearchForm())





@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
            )
            
            
            # db.session.add(user)
            # remember this right here
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)



@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    session.pop(CURR_USER_KEY)
    flash("Goodbye!", "info")
    return redirect('/')







@app.route("/")
def root():
    """Homepage!!!"""
    if g.user:

        return render_template('home.html')
    else:
        return render_template('home-anon.html')
    


def fetch_manga(genre):
    # form = SearchForm()
    print(f"SELECTED GENRE: {genre}")
    # genre = request.form.get('genre')
    # print(genre)
    querystring = {"page":"1","genres": genre}
    res = requests.get(f"{API_BASE_URL}/fetch", headers=headers, params=querystring)
    data = res.json()
    for key, val in data.items():
        print(key, val)
    mangas = data.get('data')
    return mangas



@app.route('/search_anime/<int:user_id>', methods=["GET", "POST"])
def search_anime(user_id):
    user = User.query.get_or_404(user_id)
    form = SearchForm()
    
    
    if form.validate_on_submit():
        genres = form.genre.data
        # print(genres)
        mangas = fetch_manga(genres)
        session['mangas'] = mangas
        return redirect('/called_manga', user=user,  
                        genre=genres,mangs=mangas)
    else:
        return render_template('users/anime_picker.html', form=form, user=user)


@app.route('/called_manga', methods=["GET", "POST"])
def get_manga():

    genre = request.args.get('genre')
    mangas = fetch_manga(genre)

    return render_template('users/picked_anime.html', mangas=mangas, genre=genre, form=SearchForm())
    


@app.route('/favorites/<int:user_id>')
def show_favorites(user_id):
    print()
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(user_id)
    # print(user.favorites[0].name)
    return render_template("users/favorites.html",favorites=user.favorites )

