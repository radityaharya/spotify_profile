
# Spotify Profile

A simple Flask app with Redis as caching, MongoDB as a database, Jinja as the template engine and Bootstrap CSS framework that allows user to share their Spotify profile information such as currently playing track, top artists and top tracks. This application also allows user to share a page where their friends can recommend songs by posting a link to the application and the track will then be added to a generated playlist.

A live demo is available at [spotify.radityaharya.me](https://spotify.radityaharya.me)

## Screenshots

![App Screenshot](https://raw.githubusercontent.com/radityaharya/spotify_profile/master/screenshots/1.png)

![App Screenshot](https://raw.githubusercontent.com/radityaharya/spotify_profile/master/screenshots/2.png)

## Features

- Show user's currently playing track
- Show user's top tracks
- Show user's top artist
- Allow people to add a track to a recommended playlist

## Run Locally

Clone the project

```bash
  git clone https://github.com/radityaharya/spotify_profile
```

Go to the project directory

```bash
  cd spotify_profile
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  python3 routes.py
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`HOST`

`PORT`

`MONGO_URI`

`SPOTIFY_CLIENT_ID`

`SPOTIFY_CLIENT_SECRET`

`SPOTIFY_REDIRECT_URI`

`REDIS_URL`

`REDIS_HOST`

`REDIS_PORT`

`REDIS_DB`

`REDIS_PASSWORD`

`ENCRYPTION_KEY`

## Directory Hierarchy

```
|—— .gitignore
|—— requirements.txt
|—— routes.py
|—— functions
|    |—— __init__.py
|    |—— spotify.py
|    |—— util.py
||—— templates
|    |—— 404.html
|    |—— base.jinja
|    |—— components
|        |—— navbar.jinja
|        |—— public_playlists.jinja
|        |—— top_card_artists.jinja
|        |—— top_card_tracks.jinja
|    |—— index.jinja
|    |—— settings.jinja
|    |—— user_profile.jinja
|—— static
|    |—— bootstrap
|        |—— css
|            |—— bootstrap.min.css
|    |—— css
|        |—— base.css
|    |—— img
|        |—— favicons
|            |—— android-icon-144x144.png
|            |—— android-icon-192x192.png
|            |—— android-icon-36x36.png
|            |—— android-icon-48x48.png
|            |—— android-icon-72x72.png
|            |—— android-icon-96x96.png
|            |—— apple-icon-114x114.png
|            |—— apple-icon-120x120.png
|            |—— apple-icon-144x144.png
|            |—— apple-icon-152x152.png
|            |—— apple-icon-180x180.png
|            |—— apple-icon-57x57.png
|            |—— apple-icon-60x60.png
|            |—— apple-icon-72x72.png
|            |—— apple-icon-76x76.png
|            |—— apple-icon-precomposed.png
|            |—— apple-icon.png
|            |—— favicon-16x16.png
|            |—— favicon-32x32.png
|            |—— favicon-96x96.png
|            |—— ms-icon-144x144.png
|            |—— ms-icon-150x150.png
|            |—— ms-icon-310x310.png
|            |—— ms-icon-70x70.png
|        |—— nowplaying.gif
|        |—— rick-rolled.gif
|    |—— js
|        |—— bold-and-bright.js
|        |—— lf30_editor_rtjbdghp.json
|    |—— manifest.json
```

## Feedback

If you have any feedback, please reach out to me at contact@radityaharya.me
