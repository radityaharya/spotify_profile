import os
import logging

from flask_caching import Cache
from flask import jsonify
from flask import redirect, render_template, request, url_for, session, Flask
from werkzeug.serving import WSGIRequestHandler
from rich.logging import RichHandler
import pymongo
import spotipy
from dotenv import load_dotenv

from functions import spotify
from functions import util

load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client.spotify
collection = db.spotify_users

app = Flask(__name__)

SCOPE = "user-read-private user-read-playback-state user-modify-playback-state user-library-read user-top-read user-library-modify playlist-read-private playlist-modify-private playlist-read-collaborative playlist-modify-public"
sp_oauth = spotipy.oauth2.SpotifyOAuth(
    scope=SCOPE,
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    cache_handler=None,
)

# Setting up the logger to log to a file and to the console.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(lineno)s - %(funcName)s ] %(message)s",
    handlers=[logging.FileHandler(".log"), RichHandler()],
)

logger = logging.getLogger("spotify")
logger.setLevel(logging.DEBUG)

config = {
    "DEBUG": True,
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 60,
    "CACHE_REDIS_HOST": os.getenv("REDIS_HOST"),
    "CACHE_REDIS_PORT": os.getenv("REDIS_PORT"),
    "CACHE_REDIS_URL": os.getenv("REDIS_URL"),
    "CACHE_REDIS_PASSWORD": os.getenv("REDIS_PASSWORD"),
    "CACHE_REDIS_DB": os.getenv("REDIS_DB"),
    "CACHE_KEY_PREFIX": "spotify",
    "ENV": "PRODUCTION",
}


app.config.from_mapping(config)
cache = Cache(app)


@app.route("/index")
@app.route("/")
def index():
    """
    If the user is logged in, then show the user's top page, otherwise show the login page

    Returns:
        The login page if the user is not logged in, or the user's top page if the user is logged in.
    """
    if "auth" in session:
        logger.debug(f"{session['auth']}")
        data = util.get_cookie(session)
        util.check_and_refresh_token(
            sp_oauth, collection, data["access_token"], session
        )
        logger.info(f"{data['user_info']['id']} logged in")
        return user_top_page(data["user_info"]["id"], is_base=True)
    else:
        return render_template("login.html.jinja")


@app.route("/login")
def login():
    """
    It removes the `auth` key from the session, and then redirects the user to the Spotify authorization
    page

    Returns:
      The user is being redirected to the Spotify login page.
    """
    session.pop("auth", None)
    return redirect(sp_oauth.get_authorize_url())


@app.route("/logout")
def logout():
    """
    It removes the "auth" key from the session, and then redirects the user to the index page

    Returns:
      a redirect to the index page.
    """
    session.pop("auth", None)
    return redirect(
        url_for("index"),
    )


@app.route("/callback")
def callback():
    """
    It takes the code from the query string, uses it to get an access token, generates a cookie from the
    token, and then inserts the user's id and token into the database if they're not already there

    Returns:
      A redirect to the index page.
    """
    code = request.args["code"]
    token = sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
    user_info = util.generate_cookie(session, token)["user_info"]
    logger.info(f"{user_info['id']} calledback")
    if not collection.find_one({"_id": user_info["id"]}):
        collection.insert_one(
            {
                "_id": user_info["id"],
                "user_id": user_info["id"],
                "token": util.encrypt(token),
            }
        )
    return redirect(url_for("index"))


@app.route("/<user_id>")
def user_top_page(user_id, is_base: bool = False):
    """
    It takes a user_id and a boolean value, and returns a rendered template of the user's top tracks and
    artists, as well as the currently playing song

    Args:
      user_id: The user's ID
      is_base (bool): if True, the page will be rendered with the track recommendations form disabled. Instead it will show a link to the users endpoint

    Returns:
      A rendered template of the top page for the user.
    """
    if request.args.get("track_added"):
        track_added = True
    else:
        track_added = False

    user_token = util.decrypt(collection.find_one({"_id": user_id})["token"])

    user_token = util.check_and_refresh_token(sp_oauth, collection, user_token, session)
    user = {
        "user_display_name": spotify.get_user_info(user_token["access_token"])[
            "display_name"
        ],
        "user_profile_picture": spotipy.Spotify(
            auth=user_token["access_token"]
        ).current_user()["images"][0]["url"],
        "user_id": user_id,
        "user_recommended_playlist_url": spotify.get_user_recommended_playlist(
            user_token["access_token"]
        )["external_urls"]["spotify"],
    }
    top_tracks = spotify.get_user_top_tracks(user_token["access_token"])
    top_artists = spotify.get_user_top_artists(user_token["access_token"])
    currently_playing = spotify.get_user_currently_playing(user_token["access_token"])
    if currently_playing["track_name"] == "":
        try:
            currently_playing = collection.find_one({"_id": user_id})[
                "currently_playing"
            ]
        except:
            currently_playing = {
                "track_name": "Nothing is playing",
                "track_artist": "",
                "track_album": "",
                "track_image": "",
                "track_url": "",
            }
    return render_template(
        "top.html.jinja",
        user=user,
        user_data={"top_tracks": top_tracks, "top_artists": top_artists},
        currently_playing=currently_playing,
        base=is_base,
        track_added=track_added,
    )


@app.route("/<user_id>/currently_playing")
@cache.memoize(timeout=60)
def user_currently_playing(user_id):
    """
    It gets the currently playing track for a user, and updates the database with the track information

    Args:
      user_id: the user's id

    Returns:
      The currently playing song of the user.
    """
    user_token = util.decrypt(collection.find_one({"_id": user_id})["token"])
    user_token = util.check_and_refresh_token(sp_oauth, collection, user_token, session)
    currently_playing = spotify.get_user_currently_playing(user_token["access_token"])
    collection.update_one(
        {"_id": user_id},
        {"$set": {"currently_playing": currently_playing}},
    )
    logger.info(f"{user_id} is currently playing {currently_playing['track_name']}")
    return jsonify(currently_playing)


@app.route("/<user_id>/add_to_queue", methods=["POST"])
def add_to_queue(user_id):
    """
    It takes a user id, finds the user's token, checks if the token is expired, refreshes it if it is,
    and then adds a track to the user's queue

    Args:
      user_id: the user's id

    Returns:
      The user is being redirected to the user_top_tracks page.
    """
    user_token = util.decrypt(collection.find_one({"_id": user_id})["token"])
    user_token = util.check_and_refresh_token(sp_oauth, collection, user_token, session)
    spotify_link = request.form["link"]
    spotify.add_track_to_queue(user_token["access_token"], spotify_link)
    logger.info(f"added {spotify_link} to {user_id} queue")
    return redirect(url_for("user_top_page", user_id=user_id))


@app.route("/<user_id>/add_track_to_recommended_playlist", methods=["POST"])
def add_track_to_recommended_playlist(user_id):
    """
    It takes a user id, finds the user's token, checks if the token is expired, if it is, it refreshes
    the token, then it adds the track to the user's recommended playlist.

    Args:
      user_id: the user's id

    Returns:
    The user is being redirected to the user_top_tracks page.
    """
    user_token = util.decrypt(collection.find_one({"_id": user_id})["token"])
    user_token = util.check_and_refresh_token(sp_oauth, collection, user_token, session)
    spotify.add_track_to_recommended_playlist(
        user_token["access_token"], request.form["link"]
    )
    logger.info(f"added {request.form['link']} to {user_id} playlist")
    return redirect(url_for("user_top_page", user_id=user_id, track_added=True))


# overrides the default
# WSGIRequestHandler class to make it log the IP address of the client instead
# of the IP address of the proxy server
class MyRequestHandler(WSGIRequestHandler):
    def address_string(self):
        return self.headers["X-Forwarded-For"]

    def log_date_time_string(self):
        return ""

    def log_request(self, code="-", size="-"):
        self.log_message('"%s" %s %s', self.requestline, str(code), str(size))


if __name__ == "__main__":
    app.secret_key = os.getenv("ENCRYPTION_KEY")
    logger = logging.getLogger("werkzeug")
    logger.setLevel(logging.INFO)
    app.run(
        debug=False,
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        request_handler=MyRequestHandler,
    )
