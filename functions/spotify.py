from collections import Counter
import datetime
import traceback
import spotipy
import logging

logger = logging.getLogger("spotify")
logger.setLevel(logging.DEBUG)


def get_user_info(access_token):
    """
    It takes an access token and returns the user's information

    Args:
      access_token: The access token that we got from the previous step.

    Returns:
      A dictionary with the user's information.
    """
    sp = spotipy.Spotify(auth=access_token)
    logger.debug("Getting user info for {}".format(sp.current_user()["display_name"]))
    return sp.current_user()


def get_640_image(list_of_images):
    """
    It takes a list of images and returns the URL of the image that has a width of 640 pixels

    Args:
      list_of_images: a list of dictionaries, each dictionary containing information about an image.

    Returns:
      The url of the image with a width of 640.
    """
    for image in list_of_images:
        if image["width"] == 640:
            return image["url"]


def get_user_top_tracks(access_token, collection):
    """
    It gets the user's top tracks from Spotify, and returns a list of dictionaries containing the
    track's name, artist, album, album cover, track id, and track url

    Args:
      access_token: The access token that you get from the Spotify API.

    Returns:
      A list of dictionaries.
    """
    user_id = get_user_info(access_token)["id"]
    try:
        top_tracks = collection.find_one({"_id": user_id})["top_tracks"]
        if top_tracks["datetime_added"] < datetime.datetime.now() - datetime.timedelta(
            days=4
        ):
            raise "Cache expired"
    except Exception as e:
        logger.error(e)
        sp = spotipy.Spotify(auth=access_token)
        short_term_top_tracks = sp.current_user_top_tracks(
            limit=10, offset=0, time_range="short_term"
        )
        medium_term_top_tracks = sp.current_user_top_tracks(
            limit=10, offset=0, time_range="medium_term"
        )
        long_term_top_tracks = sp.current_user_top_tracks(
            limit=10, offset=0, time_range="long_term"
        )
        top_tracks = {
            "short_term": [
                {
                    "number": short_term_top_tracks["items"].index(track) + 1,
                    "track_name": track["name"],
                    "artist_name": track["artists"][0]["name"],
                    "album_name": track["album"]["name"],
                    "album_cover": get_640_image(track["album"]["images"]),
                    "track_id": track["id"],
                    "track_url": track["external_urls"]["spotify"],
                }
                for track in short_term_top_tracks["items"]
            ],
            "medium_term": [
                {
                    "number": medium_term_top_tracks["items"].index(track) + 1,
                    "track_name": track["name"],
                    "artist_name": track["artists"][0]["name"],
                    "album_name": track["album"]["name"],
                    "album_cover": get_640_image(track["album"]["images"]),
                    "track_id": track["id"],
                    "track_url": track["external_urls"]["spotify"],
                }
                for track in medium_term_top_tracks["items"]
            ],
            "long_term": [
                {
                    "number": long_term_top_tracks["items"].index(track) + 1,
                    "track_name": track["name"],
                    "artist_name": track["artists"][0]["name"],
                    "album_name": track["album"]["name"],
                    "album_cover": get_640_image(track["album"]["images"]),
                    "track_id": track["id"],
                    "track_url": track["external_urls"]["spotify"],
                }
                for track in long_term_top_tracks["items"]
            ],
            "datetime_added": datetime.datetime.now(),
        }
        try:
            collection.insert_one({"_id": user_id, "top_tracks": top_tracks})
        except Exception as e:
            collection.update_one(
                {"_id": user_id}, {"$set": {"top_tracks": top_tracks}}
            )
        top_tracks = collection.find_one({"_id": user_id})["top_tracks"]
    return top_tracks


def get_user_top_artists(access_token, collection):
    """
    > This function takes in an access token and returns a list of dictionaries containing the top 10
    artists of the user

    Args:
      access_token: the access token we got from the previous step

    Returns:
      A list of dictionaries.
    """
    user_id = get_user_info(access_token)["id"]
    try:
        top_artists = collection.find_one({"_id": user_id})["top_artists"]
        if top_artists["datetime_added"] < datetime.datetime.now() - datetime.timedelta(
            days=4
        ):
            raise "Cache expired"
    except Exception as e:
        logger.error(e)
        sp = spotipy.Spotify(auth=access_token)
        short_term_top_artists = sp.current_user_top_artists(
            limit=10, offset=0, time_range="short_term"
        )
        medium_term_top_artists = sp.current_user_top_artists(
            limit=10, offset=0, time_range="medium_term"
        )
        long_term_top_artists = sp.current_user_top_artists(
            limit=10, offset=0, time_range="long_term"
        )
        top_artists = {
            "short_term": [
                {
                    "number": short_term_top_artists["items"].index(item) + 1,
                    "artist_name": item["name"],
                    "artist_id": item["id"],
                    "artist_url": item["external_urls"]["spotify"],
                    "artist_image": get_640_image(item["images"]),
                    "followers": item["followers"]["total"],
                }
                for item in short_term_top_artists["items"]
            ],
            "medium_term": [
                {
                    "number": medium_term_top_artists["items"].index(item) + 1,
                    "artist_name": item["name"],
                    "artist_id": item["id"],
                    "artist_url": item["external_urls"]["spotify"],
                    "artist_image": get_640_image(item["images"]),
                    "followers": item["followers"]["total"],
                }
                for item in medium_term_top_artists["items"]
            ],
            "long_term": [
                {
                    "number": long_term_top_artists["items"].index(item) + 1,
                    "artist_name": item["name"],
                    "artist_id": item["id"],
                    "artist_url": item["external_urls"]["spotify"],
                    "artist_image": get_640_image(item["images"]),
                    "followers": item["followers"]["total"],
                }
                for item in long_term_top_artists["items"]
            ],
            "datetime_added": datetime.datetime.now(),
        }
        try:
            collection.insert_one({"_id": user_id, "top_artists": top_artists})
        except Exception as e:
            collection.update_one(
                {"_id": user_id}, {"$set": {"top_artists": top_artists}}
            )
        top_artists = collection.find_one({"_id": user_id})["top_artists"]
    return top_artists


def get_user_currently_playing(access_token):
    """
    It takes an access token, uses it to create a Spotify object, then uses that object to get the
    currently playing track. If there is a currently playing track, it returns a dictionary with the
    track's name, artist, album, album cover, track id, and track url. If there is no currently playing
    track, it returns a dictionary with empty strings for all of the values

    Args:
      access_token: The access token that you get from the Spotify API.

    Returns:
      A dictionary with the following keys:
        track_name
        artist_name
        album_name
        album_cover
        track_id
        track_url
        datetime_added
    """
    sp = spotipy.Spotify(auth=access_token)
    data = sp.current_user_playing_track()
    datetime_added = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if data:
        currently_playing = {
            "track_name": data["item"]["name"],
            "artist_name": data["item"]["artists"][0]["name"],
            "album_name": data["item"]["album"]["name"],
            "album_cover": get_640_image(data["item"]["album"]["images"]),
            "track_id": data["item"]["id"],
            "track_url": data["item"]["external_urls"]["spotify"],
            "datetime_added": datetime_added,
        }
    else:
        currently_playing = {
            "track_name": "",
            "artist_name": "",
            "album_name": "",
            "album_cover": "",
            "track_id": "",
            "track_url": "",
            "datetime_added": datetime_added,
        }
    logger.info(
        "Got currently playing for {}".format(sp.current_user()["display_name"])
    )
    return currently_playing


def get_uri_from_track_url(track_url):
    """
    It takes a Spotify track URL and returns the URI of the track

    Args:
      track_url: The URL of the track you want to add to the playlist.

    Returns:
      A list of track URIs
    """
    track_url = track_url.split("?")[0]
    track_id = track_url.split("/")[4]
    uri = "spotify:track:" + track_id
    return uri


def add_track_to_queue(access_token, track_url):
    """
    It takes a track URL and adds it to the user's queue

    Args:
      access_token: The access token you got from the previous step.
      track_url: The URL of the track you want to add to the queue.

    Returns:
      A dictionary with the following keys:
        'snapshot_id'
        'tracks'
    """
    sp = spotipy.Spotify(auth=access_token)
    uri = get_uri_from_track_url(track_url)
    return sp.add_to_queue(uri)


def get_user_public_playlists(access_token, collection):
    """
    It gets the user's public playlists and returns a list of dictionaries containing the playlist's
    name, playlist id, and playlist url

    Args:
      access_token: The access token that you get from the Spotify API.

    Returns:
      A list of dictionaries.
    """
    user_id = get_user_info(access_token)["id"]
    try:
        playlists = collection.find_one({"_id": user_id})["playlists"]
        if playlists["datetime_added"] < datetime.datetime.now() - datetime.timedelta(
            days=4
        ):
            raise "Cache expired"
    except Exception as e:
        logger.error(traceback.format_exc())
        sp = spotipy.Spotify(auth=access_token)
        data = sp.current_user_playlists()
        public_playlists = [
            {
                "number": data["items"].index(item) + 1,
                "playlist_name": item["name"],
                "playlist_id": item["id"],
                "playlist_url": item["external_urls"]["spotify"],
                "playlist_picture": item["images"][0]["url"],
                "playlist_like_count": sp.playlist(item["id"])["followers"]["total"],
            }
            for item in data["items"]
            if item["public"]
        ]
        playlists = {
            "playlists": public_playlists,
            "datetime_added": datetime.datetime.now(),
        }
        try:
            collection.insert_one({"_id": user_id, "playlists": playlists})
        except Exception as e:
            collection.update_one({"_id": user_id}, {"$set": {"playlists": playlists}})
        playlists = collection.find_one({"_id": user_id})["playlists"]
        logger.debug(data)
        logger.info(
            "Got public playlists for {}".format(sp.current_user()["display_name"])
        )
    public_playlists = collection.find_one({"_id": user_id})["playlists"]
    return public_playlists


def get_user_recommended_playlist(access_token):
    """
    Get the user's "Recommended Tracks" playlist, or create one if it doesn't exist

    Args:
      access_token: The access token you got from the authorization step.

    Returns:
      A dictionary containing the playlist information
    """
    sp = spotipy.Spotify(auth=access_token)
    user_id = get_user_info(access_token)["id"]
    playlists = sp.user_playlists(user_id)["items"]
    for playlist in playlists:
        if playlist["name"] == "Recommended Tracks":
            return playlist
    new_playlist_id = sp.user_playlist_create(
        user_id, "Recommended Tracks", public=False
    )["id"]
    sp.user_playlist_change_details(
        user_id,
        new_playlist_id,
        description="Generated Playlist from https://spotify.radityaharya.me",
    )
    return sp.user_playlist(user_id, new_playlist_id)


def add_track_to_recommended_playlist(access_token, track_url):
    """
    > It takes a track url and adds it to the user's recommended playlist

    Args:
      access_token: The access token you got from the authorization flow.
      track_url: The url of the track you want to add to the playlist.

    Returns:
      A dictionary with the following keys:
        snapshot_id
        tracks
    """
    sp = spotipy.Spotify(auth=access_token)
    logger.info(f"Adding track to recommended playlist: {track_url}")
    return sp.user_playlist_add_tracks(
        get_user_info(access_token)["id"],
        get_user_recommended_playlist(access_token)["id"],
        [get_uri_from_track_url(track_url)],
    )


def get_user_top_genres(access_token, collection, limit=100):
    """
    It gets the user's top genres

    Args:
      access_token: The access token you got from the authorization step.

    Returns:
      A list of dictionaries containing the genre name and genre id
    """
    user_id = get_user_info(access_token)["id"]
    try:
        top_genres = collection.find_one({"_id": user_id})["top_genres"]
        if top_genres["datetime_added"] < datetime.datetime.now() - datetime.timedelta(
            days=4
        ):
            raise "Cache expired"
    except Exception as e:
        logger.error(e)
        sp = spotipy.Spotify(auth=access_token)
        short_term_data = sp.current_user_top_artists(
            limit=limit, time_range="short_term"
        )["items"]
        medium_term_data = sp.current_user_top_artists(
            limit=limit, time_range="medium_term"
        )["items"]
        long_term_data = sp.current_user_top_artists(
            limit=limit, time_range="long_term"
        )["items"]
        data = short_term_data + medium_term_data + long_term_data
        genres = [item["genres"] for item in data]
        genres = [item for sublist in genres for item in sublist]
        genres = Counter(genres)
        genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
        genres = [
            {"name": item[0], "number_of_occcurences": item[1]} for item in genres
        ]
        top_genres = {"datetime_added": datetime.datetime.now(), "genres": genres}
        try:
            collection.insert_one({"_id": user_id, "top_genres": top_genres})
        except Exception as e:
            logger.error(e)
            collection.update_one(
                {"_id": user_id}, {"$set": {"top_genres": top_genres}}
            )
        top_genres = collection.find_one({"_id": user_id})["top_genres"]
    return top_genres


def get_user_recently_played(access_token, collection, limit=50):
    """
    It gets the user's recently played tracks

      Args:
        access_token: The access token you got from the authorization step.
        limit: The number of tracks to return.

      returns:
        A list of dictionaries containing the track name, artist name, album name, album picture, and track url
    """
    user_id = get_user_info(access_token)["id"]
    try:
        recently_played = collection.find_one({"_id": user_id})["recently_played"]
        if recently_played[
            "datetime_added"
        ] < datetime.datetime.now() - datetime.timedelta(days=4):
            raise "Cache expired"
    except Exception as e:
        logger.error(e)
        sp = spotipy.Spotify(auth=access_token)
        data = sp.current_user_recently_played(limit=limit)["items"]
        recently_played = [
            {
                "track_id": item["track"]["id"],
                "track_name": item["track"]["name"],
                "artist_name": item["track"]["artists"][0]["name"],
                "album_name": item["track"]["album"]["name"],
                "album_picture": item["track"]["album"]["images"][0]["url"],
                "track_url": item["track"]["external_urls"]["spotify"],
                "datetime_played": item["played_at"],
            }
            for item in data
        ]
        try:
            collection.insert_one({"_id": user_id, "recently_played": recently_played})
        except Exception as e:
            logger.error(e)
            collection.update_one(
                {"_id": user_id}, {"$set": {"recently_played": recently_played}}
            )
        recently_played = collection.find_one({"_id": user_id})["recently_played"]
    return recently_played
