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

from six.moves.urllib.parse import urlencode
from .core import SessionToken, Parse
from .objects import ParseObject


class User(ParseObject):
    __name__ = "_User"

    PROTECTED_ATTRIBUTES = ParseObject.PROTECTED_ATTRIBUTES + ['username', 'sessionToken',
                                                               'emailVerified']
    @staticmethod
    def become(session_token):
        with SessionToken(session_token):
            options = {
                'route': 'users',
                'objectId': 'me',
                'method': 'GET'
            }

            response = Parse.Initialization.request(**options)

        user = User()
        ParseObject.convert_from_parse_to_native(response, item=user)

        return user

    @staticmethod
    def login(username, password):
        options = {
            'route': 'login',
            'method': 'GET',
            'params': urlencode({'username': username, 'password': password})
        }

        response = Parse.Initialization.request(**options)

        user = User()
        ParseObject.convert_from_parse_to_native(response, item=user, is_loaded=True)

        return user

    @staticmethod
    def signup(username, password):
        options = {
            'route': 'users',
            'method': 'POST',
            'data': {'username': username, 'password': password}
        }

        response = Parse.Initialization.request(**options)

        user = User()
        ParseObject.convert_from_parse_to_native(response, item=user, is_loaded=True)

        return user

    def save(self):
        with SessionToken(self.sessionToken):
            options = {
                'route': 'users',
                'objectId': self.objectId,
                'method': 'PUT',
                'data': dict((k, v) for k, v in self._convert_from_native_to_parse().items() if
                             k in self._dirty_keys)
            }

            response = Parse.Initialization.request(**options)

        ParseObject.convert_from_parse_to_native(response, item=self, is_loaded=True)
        self._dirty_keys.clear()

    def delete(self):
        with SessionToken(self.sessionToken):
            options = {
                'route': 'users',
                'objectId': self.objectId,
                'method': 'DELETE'
            }

            response = Parse.Initialization.request(**options)

    @property
    def className(self):
        return '_User'

    def __repr__(self):
        return '<User:%s (Id %s)>' % (getattr(self, 'username', None), self.objectId)