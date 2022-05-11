import datetime
import spotipy


def get_user_info(access_token):
    """
    It takes an access token and returns the user's information

    Args:
      access_token: The access token that we got from the previous step.

    Returns:
      A dictionary with the user's information.
    """
    sp = spotipy.Spotify(auth=access_token)
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


def get_user_top_tracks(access_token):
    """
    It gets the user's top tracks from Spotify, and returns a list of dictionaries containing the
    track's name, artist, album, album cover, track id, and track url

    Args:
      access_token: The access token that you get from the Spotify API.

    Returns:
      A list of dictionaries.
    """
    sp = spotipy.Spotify(auth=access_token)
    data = sp.current_user_top_tracks(limit=10, offset=0, time_range="short_term")
    if len(data["items"]) < 1:
        data = sp.current_user_top_tracks(limit=10, offset=0, time_range="long_term")
    items = data["items"]
    top_tracks = [
        {
            "number": items.index(item) + 1,
            "track_name": item["name"],
            "artist_name": item["artists"][0]["name"],
            "album_name": item["album"]["name"],
            "album_cover": get_640_image(item["album"]["images"]),
            "track_id": item["id"],
            "track_url": item["external_urls"]["spotify"],
        }
        for item in items
    ]
    return top_tracks


def get_user_top_artists(access_token):
    """
    > This function takes in an access token and returns a list of dictionaries containing the top 10
    artists of the user

    Args:
      access_token: the access token we got from the previous step

    Returns:
      A list of dictionaries.
    """
    sp = spotipy.Spotify(auth=access_token)
    data = sp.current_user_top_artists(limit=10, offset=0, time_range="short_term")
    if len(data["items"]) < 1:
        data = sp.current_user_top_artists(limit=10, offset=0, time_range="long_term")
    items = data["items"]
    top_artists = [
        {
            "number": items.index(item) + 1,
            "artist_name": item["name"],
            "artist_picture": item["images"][0]["url"],
            "followers": item["followers"]["total"],
            "artist_id": item["id"],
            "artist_url": item["external_urls"]["spotify"],
        }
        for item in items
    ]
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
    return sp.user_playlist_add_tracks(
        get_user_info(access_token)["id"],
        get_user_recommended_playlist(access_token)["id"],
        [get_uri_from_track_url(track_url)],
    )
