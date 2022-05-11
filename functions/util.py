import json
import os
from cryptography.fernet import Fernet
from functions import spotify
import logging

logger = logging.getLogger("spotify")
logger.setLevel(logging.DEBUG)


def encrypt(data):
    if os.getenv("ENCRYPTION_KEY"):
        key = os.getenv("ENCRYPTION_KEY")
        key = bytes(key, "utf-8")
    else:
        key = Fernet.generate_key()
        with open(".env", "a") as f:
            f.write(f'\nENCRYPTION_KEY= "{key.decode()}"')

    print(key)
    fernet = Fernet(key)

    if isinstance(data, dict):
        data = json.dumps(data)

    return fernet.encrypt(data.encode())


def decrypt(data):
    key = os.getenv("ENCRYPTION_KEY")
    key = bytes(key, "utf-8")

    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(data).decode()

    if decrypted_data.startswith("{"):
        decrypted_data = json.loads(decrypted_data)
    return decrypted_data


def generate_cookie(session, token):
    """
    It takes a token, gets the user's info, util.encrypts it, and stores it in a cookie

    Args:
      token: The token object returned from the Spotify API

    Returns:
      The data is being returned.
    """
    user_info = spotify.get_user_info(token["access_token"])
    logger.info(f"User {user_info['id']} cookie generated")
    data = {"user_info": user_info, "access_token": token}
    session["auth"] = encrypt(data)
    return data


def get_cookie(session):
    """
    It util.decrypts the cookie, and returns the util.decrypted data

    Returns:
      The data is being returned.
    """
    data = decrypt(session["auth"])
    return data


def check_and_refresh_token(sp_oauth, collection, access_token, session):
    """
    If the token is expired, refresh it and update the database

    Args:
      access_token: The access token of the user.

    Returns:
      The refreshed token.
    """
    if sp_oauth.is_token_expired(access_token):
        access_token = sp_oauth.refresh_access_token(access_token["refresh_token"])
        user_id = spotify.get_user_info(access_token["access_token"])["id"]
        collection.update_one(
            {"_id": user_id}, {"$set": {"token": encrypt(access_token)}}
        )
        generate_cookie(session, access_token)
        logger.info(f"Token refreshed for user {user_id}")
        return access_token
    logger.info(f"Token is still valid for user {access_token}")
    return access_token
