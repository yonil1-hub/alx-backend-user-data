#!/usr/bin/env python3
"""
0-user model
"""


from sqlalchemy import Column, Integer, String, orm


Base = orm.declarative_base()

class User(Base):
    """
    User table defination.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True)
    reset_token = Column(String(250), nullable=True)