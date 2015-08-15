from requests import request
import json
from .exceptions import ParseException
import logging


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
            cls.Initialization.rest_api_id = args[1]
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
        class_name = kwargs.get('class_name', None)
        objectId = kwargs.get('objectId', None)
        method = kwargs.get('method', 'get')
        data = kwargs.get('data', None)

        if route not in Parse.allowed_routes:
            raise Exception  # todo

        url = Parse.server_url + route

        if class_name is not None:
            url += '/' + class_name

        if objectId is not None:
            url += '/' + objectId

        headers = {
            'Content-type': 'application/json',
            'X-Parse-Application-Id': self.application_id,
            'X-Parse-REST-API-Key': self.rest_api_key
        }

        return self._send(url, json.dumps(data), method, headers)

    def _send(self, url, data, method, headers):
        attempts = 1
        error = None
        while attempts <= Parse.max_attempts:
            try:
                response = request(url=url, data=data, method=method, headers=headers)
            except Exception as e:
                Parse.Logger.exception(e)
                error = e
                attempts += 1
            else:
                return response.json()

        # return the error from the latest attempt
        raise self.get_exception(error)

    def batch(self):
        raise NotImplemented

    def get_exception(self, e):
        return Exception
