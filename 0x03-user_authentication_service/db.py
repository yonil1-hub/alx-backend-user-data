#!/usr/bin/env python3
""" Database for ORM """

from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import session
from typing import TypeVar
from user import Base, User


class DB:
    """
    DB Class for Object Relational Mapping

    Attributes:
    -----------
    _engine : sqlalchemy.engine.Engine
        The engine object that manages database connections.
    __session : sqlalchemy.orm.Session
        The session object that represents a transaction with the database.
    """

    def __init__(self):
        """
        Constructor Method

        Initializes the database engine, creates the tables if they
        don't exist,and sets the session object to None.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> session:
        """
        Session Getter Method

        Creates a new session if it does not exist, and returns the existing
        session otherwise.

        Returns:
        --------
        sqlalchemy.orm.Session
            The session object that represents a transaction with the database.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Adds a new user to the database.

        Parameters:
        -----------
        email : str
            The email address of the user.
        hashed_password : str
            The hashed password of the user.

        Returns:
        --------
        User
            The User object that represents the newly added user.
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()

        return user

    def find_user_by(self, **kwargs) -> User:
        """
        Finds a user in the database that matches the given criteria.

        Parameters:
        -----------
        **kwargs : dict
            Keyword arguments that specify the search criteria.
            The keys must be attribute names of the User class.

        Returns:
        --------
        User
            The User object that matches the given criteria.

        Raises:
        -------
        InvalidRequestError
            If no search criteria are specified or if any of the
            search criteria are not valid attribute names of the User class.
        NoResultFound
            If no user is found that matches the given criteria.
        """
        if not kwargs:
            raise InvalidRequestError("No search criteria specified")

        column_names = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in column_names:
                message = "is not a valid search criterion"
                raise InvalidRequestError(f"{key}" + message)

        user = self._session.query(User).filter_by(**kwargs).first()

        if user is None:
            message = "No user found that matches the given criteria"
            raise NoResultFound(message)

        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Updates one or more attributes of a user in the database.

        Parameters:
        -----------
        user_id : int
            The ID of the user to be updated.
        **kwargs : dict
            Keyword arguments that specify the attributes to be
            updated and their new values.
            The keys must be attribute names of the User class.

        Returns:
        --------
        None

        Raises:
        -------
        ValueError
            If any of the keyword arguments are not valid
            attribute names of the User class.
        NoResultFound
            If no user is found with the given ID.
        """
        user = self.find_user_by(id=user_id)

        column_names = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in column_names:
                raise ValueError(f"{key} is not a valid attribute name")

        for key, value in kwargs.items():
            setattr(user, key, value)

        self._session.commit()
