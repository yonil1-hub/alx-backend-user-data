#!/usr/bin/env python3
""" Authentication Module """

import bcrypt
from db import DB
from sqlalchemy.orm.exc import NoResultFound
from typing import Union
from user import User
from uuid import uuid4


def _hash_password(password: str) -> str:
    """
    Returns a salted hash of the input password.

    Parameters:
    -----------
    password : str
        The plaintext password to be hashed.

    Returns:
    --------
    str
        The salted hash of the input password.
    """
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed


def _generate_uuid() -> str:
    """
    Generates a new UUID and returns its string representation.

    Returns:
    --------
    str
        The string representation of the newly generated UUID.
    """
    UUID = uuid4()
    return str(UUID)


class Auth:
    """
    Auth class to interact with the authentication database.

    Attributes:
    -----------
    _db : DB
        The database object used to interact with the user table.
    """

    def __init__(self):
        """
        Constructor Method

        Initializes the database object.
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Registers a new user in the database.

        Parameters:
        -----------
        email : str
            The email address of the user.
        password : str
            The plaintext password of the user.

        Returns:
        --------
        User
            The User object that represents the newly registered user.

        Raises:
        -------
        ValueError
            If a user with the same email address
            already exists in the database.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            hashed_password = _hash_password(password)
            user = self._db.add_user(email, hashed_password)
            return user
        else:
            raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """
        Checks if the given email and password correspond to a valid user.

        Parameters:
        -----------
        email : str
            The email address of the user.
        password : str
            The plaintext password to be checked.

        Returns:
        --------
        bool
            True if the email and password correspond to a valid user,
            False otherwise.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False

        user_password = user.hashed_password
        encoded_password = password.encode()

        if bcrypt.checkpw(encoded_password, user_password):
            return True

        return False

    def create_session(self, email: str) -> Union[str, None]:
        """
        Creates a new session ID for the given user.

        Parameters:
        -----------
        email : str
            The email address of the user.

        Returns:
        --------
        Union[str, None]
            The session ID string if the user is found, None otherwise.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None

        session_id = _generate_uuid()

        self._db.update_user(user.id, session_id=session_id)

        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """
        Retrieves the user associated with the given session ID.

        Parameters:
        -----------
        session_id : str
            The session ID string.

        Returns:
        --------
        Union[User, None]
            The User object associated with the given session ID if found,
            None otherwise.
        """
        if session_id is None:
            return None

        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

        return user

    def destroy_session(self, user_id: int) -> None:
        """
        Destroys the session associated with the given user ID.

        Parameters:
        -----------
        user_id : int
            The ID of the user whose session is to be destroyed.

        Returns:
        --------
        None
        """
        try:
            user = self._db.find_user_by(id=user_id)
        except NoResultFound:
            return None

        self._db.update_user(user.id, session_id=None)

        return None

    def get_reset_password_token(self, email: str) -> str:
        """
        Generates a reset password token for the given user.

        Parameters:
        -----------
        email : str
            The email address of the user.

        Returns:
        --------
        str
            The reset password token string.

        Raises:
        -------
        ValueError
            If no user with the given email address is found in the database.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError

        reset_token = _generate_uuid()

        self._db.update_user(user.id, reset_token=reset_token)

        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Updates the password of the user associated with the
        given reset password token.

        Parameters:
        -----------
        reset_token : str
            The reset password token string.
        password : str
            The new plaintext password.

        Returns:
        --------
        None

        Raises:
        -------
        ValueError
            If no user with the given reset password token
            is found in the database.
        """
        if reset_token is None or password is None:
            return None

        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        hashed_password = _hash_password(password)
        self._db.update_user(
                             user.id,
                             hashed_password=hashed_password,
                             reset_token=None)
