
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
|—— templates
|    |—— base.html.jinja
|    |—— login.html.jinja
|    |—— top.html.jinja
|—— static
|    |—— bootstrap
|        |—— css
|            |—— bootstrap.min.css
|        |—— js
|            |—— bootstrap.min.js
```

## Feedback

If you have any feedback, please reach out to me at contact@radityaharya.me
