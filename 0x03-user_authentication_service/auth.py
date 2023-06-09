#!/usr/bin/env python3

"""
Auth module
"""

import bcrypt
from db import DB
from sqlalchemy.orm.exc import NoResultFound
from user import User
import uuid


def _hash_password(password: str) -> bytes:
    """
    Returns the hased value of `password`
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def _generate_uuid() -> str:
    """
    Generates string representation of a new uuid
    """
    id = uuid.uuid4()
    return str(id)


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        """ Initialize instance """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Registers a new user
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f'User {email} already exists')
        except NoResultFound:
            pass
        return self._db.add_user(email, _hash_password(password))

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validates `email` and `password` for loggin in
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password)

    def create_session(self, email: str) -> str:
        """
        Creates a new session id for the user
        """
        id = _generate_uuid()
        try:
            user = self._db.find_user_by(email=email)
        except Exception:
            return
        self._db.update_user(user.id, session_id=id)
        return id

    def get_user_from_session_id(self, session_id: str) -> User:
        """
        Returns the user defined by `session_id`
        """
        if session_id is None:
            return
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except Exception:
            return None

    def destroy_session(self, user_id: str):
        """
        Destroys a session for logging out
        """
        if user_id is None:
            return
        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """
        Generates a reset_passowrd token for the user specified by `email`
        """
        if email is None:
            return
        try:
            user = self._db.find_user_by(email=email)
            id = _generate_uuid()
            self._db.update_user(user.id, reset_token=id)
            return id
        except Exception:
            raise ValueError

    def update_password(self, reset_token: str, password: str):
        """
        Updates password for a user having the specified `reset_token`
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            self._db.update_user(user.id,
                                 hashed_password=_hash_password(password),
                                 reset_token=None)
        except Exception:
            raise ValueError
