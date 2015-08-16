from .objects import ParseObject
from .core import SessionToken, Parse
import urllib


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
        user._load_from_parse(response)

        return user

    @staticmethod
    def login(username, password):
        options = {
            'route': 'login',
            'method': 'GET',
            'params': urllib.urlencode({'username': username, 'password': password})
        }

        response = Parse.Initialization.request(**options)

        user = User()
        user._load_from_parse(response)

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
        user._load_from_parse(response)

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

        self._load_from_parse(response)
        self._dirty_keys.clear()

    def delete(self):
        with SessionToken(self.sessionToken):
            options = {
                'route': 'users',
                'objectId': self.objectId,
                'method': 'DELETE'
            }

            response = Parse.Initialization.request(**options)

        for k, v in self.__dict__.items():
            delattr(self, k)


    @property
    def className(self):
        return '_User'

    def __repr__(self):
        return '<User:%s (Id %s)>' % (getattr(self, 'username', None), self.objectId)