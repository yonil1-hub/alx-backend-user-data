#!/usr/bin/env python3
"""
Manage API authentication system
"""
from typing import List, TypeVar
from flask import request


class Auth:
    """
    Class to manage API authentication methods
    """
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """
        Check if authentication is required for the given path
        """
        if path is None or excluded_paths is None or not len(excluded_paths):
            return True

        if path[-1] != '/':
            path += '/'
        if excluded_paths[-1] != '/':
            excluded_paths += '/'

        asterisks = [star[:-1] for star in excluded_paths if star[-1] == '*']

        for star in asterisks:
            if path.startswith(star):
                return False

        if path in excluded_paths:
            return False
        return True

    def authorization_header(self, request=None) -> str:
        """
        Retrieve the Authorization header from the request
        """
        if request is None or 'Authorization' not in request.headers:
            return None
        return request.headers.get('Authorization')

    def current_user(self, request=None) -> TypeVar('User'):
        """
        Retrieve the current user based on the request
        """
        return None
