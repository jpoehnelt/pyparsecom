from requests import request
from exceptions import ParseException

__parse_initialization = None


class Parse:
    server_url = 'https://api.parse.com/1/'
    allowed_routes = ['batch', 'classes', 'events', 'files', 'functions', 'login', 'logout', 'push', 'requestPasswordRest'
        'rest_verify_analytics', 'users', 'jobs', 'config', 'sessions', 'upgradeToRevocableSession']
    max_attempts = 5

    def __init__(self, application_id, rest_api_key, session_token=None, master_key=None):
        self.application_id = application_id
        self.rest_api_key = rest_api_key
        self.master_key = master_key
        __parse_initialization = self

    def request(self, **kwargs):
        route = kwargs.get('route', None)
        class_name = kwargs.get('class_name', None)
        object_id = kwargs.get('object_id', None)
        method = kwargs.get('method', 'get')
        data = kwargs.get('data', None)

        if route not in Parse.allowed_routes:
            raise Exception #todo

        url = Parse.server_url + route

        if class_name is not None:
            url += '/' + class_name

        if object_id is not None:
            url += '/' + object_id

        headers = {
            'Content-type': 'application/json',
            'X-Parse-Application-Id': self.application_id,
            'X-Parse-REST-API-Key': self.rest_api_key
        }

        return self._send(url, data, method, headers)

    def _send(self, url, data, method, headers):
        attempts = 0
        error = None
        while ++attempts < Parse.max_attempts:
            try:
                response = request(url=url, data=data, method=method, headers=headers)
            except Exception as e:
                error = e
            else:
                return response

        # return the error from the last attempt
        return ParseException()

    def batch(self):
        raise NotImplemented



if __name__ == "__main__":
    p = Parse('w32obnqOXh5n61OTuXIAbRZRj73oyEWCDuMBOQQu', 'ZjCmqLRivFF16Ei8PV044XU0VgoqNL34wuvI4NQ7')
    p.request()