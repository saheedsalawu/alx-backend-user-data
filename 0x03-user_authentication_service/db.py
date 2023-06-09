#!/usr/bin/env python3

"""
DB module
"""

import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from user import Base, User


class DB:
    """
    DB class
    """

    def __init__(self) -> None:
        """
        Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db",
                                     echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Adds a new user tothe database
        """
        user = User()
        user.email = email
        user.hashed_password = hashed_password
        session = self._session
        session.add(user)
        session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """
        Finds a user by columns defined in `kwargs`
        """
        if kwargs is None:
            raise InvalidRequestError
        if len(kwargs) == 0:
            raise InvalidRequestError
        for key in kwargs.keys():
            if key not in User.__dict__.keys():
                raise InvalidRequestError
        # email = kwargs.get('email')
        response = self._session.query(User).filter_by(**kwargs)
        if len(list(response)) == 0:
            raise NoResultFound
        return list(response)[0]

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Updates a user identified by `user_id`
        """
        if user_id is None:
            return
        user = self.find_user_by(id=user_id)
        for key in kwargs:
            if key not in User.__dict__.keys():
                raise ValueError
        for key, value in kwargs.items():
            user.__setattr__(key, value)
        self._session.add(user)
        self._session.commit()
