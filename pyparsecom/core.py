# Copyright (c) 2015 Justin Poehnelt
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from requests import request
import logging
import json
from .exceptions import ParseError, ParseResourceException


class Parse:
    """
    Singleton class for initialization and handling parse rest api requests
    """
    server_url = 'https://api.parse.com/1/'
    allowed_routes = ['batch', 'classes', 'events', 'files', 'functions', 'login', 'logout', 'push',
                      'requestPasswordRest' 'rest_verify_analytics', 'users', 'jobs', 'config',
                      'sessions', 'upgradeToRevocableSession']
    max_attempts = 5

    Initialization = None
    Logger = None

    def __init__(self, application_id, rest_api_key, master_key=None):
        self.application_id = application_id
        self.rest_api_key = rest_api_key
        self.master_key = master_key

    @classmethod
    def initialize(cls, *args, **kwargs):
        if cls.Initialization is None:
            cls.Initialization = Parse(*args, **kwargs)
        else:
            cls.Initialization.application_id = args[0]
            cls.Initialization.rest_api_key = args[1]
            for k, v in kwargs.items():
                setattr(cls, k, v)

        if Parse.Logger is None:
            Parse.Logger = logging.getLogger()

            Parse.Logger.setLevel(logging.DEBUG)

            log_handler = logging.StreamHandler()
            log_handler.setLevel(logging.DEBUG)
            Parse.Logger.addHandler(log_handler)

        return cls.Initialization

    def request(self, **kwargs):
        route = kwargs.get('route', None)
        className = kwargs.get('className', None)
        params = kwargs.get('params', None)
        objectId = kwargs.get('objectId', None)
        method = kwargs.get('method', 'get')
        data = kwargs.get('data', None)

        if route not in Parse.allowed_routes:
            raise ParseResourceException('%s is not allowed' % route)

        url = Parse.server_url + route

        if className is not None:
            url += '/' + className

        if objectId is not None:
            url += '/' + objectId

        if params is not None:
            url += '?%s' % params


        headers = {
            'Content-type': 'application/json',
            'X-Parse-Application-Id': self.application_id,
            'X-Parse-REST-API-Key': self.rest_api_key
        }

        if hasattr(self, 'session_token'):
            headers['X-Parse-Session-Token'] = self.session_token
        elif hasattr(self, 'master_key'):
            headers['X-Parse-Master-Key'] = self.master_key

        return self._send(url, json.dumps(data), method, headers)

    def _send(self, url, data, method, headers):
        attempts = 1
        error = None
        while attempts <= Parse.max_attempts:
            try:
                response = request(url=url, data=data, method=method, headers=headers)
            except Exception as e:
                Parse.Logger.debug(e)
                error = e
                attempts += 1
            else:
                if response.status_code not in [200, 201]:
                    raise ParseError(**response.json())

                return response.json()

        # return the error from the latest attempt
        raise error

    def batch(self):
        raise NotImplemented

    @classmethod
    def get_initialization(cls):
        return cls.Initialization

class SessionToken:
    def __init__(self, session_token):
        self.session_token = session_token

    def __enter__(self):
        Parse.Initialization.session_token = self.session_token

    def __exit__(self, *args, **kwargs):
        del Parse.Initialization.session_token


class MasterKey:
    def __init__(self, master_key):
        self.master_key = master_key

    def __enter__(self):
        Parse.Initialization.master = self.master_key

    def __exit__(self, *args, **kwargs):
        del Parse.Initialization.master_key