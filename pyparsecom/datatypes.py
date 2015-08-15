from .core import Parse


class ParseObject(object):
    meta = ['_data', '_is_dirty', 'objectId', 'createdAt', 'updatedAt']
    class_map = {}

    def __init__(self, **kwargs):
        self._is_dirty = True
        self._data = {}

        for k, v in kwargs.items():
            setattr(self, k, v)

    def fetch(self):
        if not hasattr(self, 'objectId'):
            raise Exception # cannot fetch without id

        options = {
            'route': 'classes',
            'class_name': self.__class__.__name__,
            'method': 'GET',
            'objectId': self.objectId
        }

        response = Parse.Initialization.request(**options)
        print response
        self._convert_from_parse(response)

    def save(self):
        options = {
            'route': 'classes',
            'class_name': self.__class__.__name__,
            'method': 'POST',
            'data': self._data
        }

        if hasattr(self, 'objectId'):
            options['method'] = 'PUT'
            options['objectId'] = self.objectId

        response = Parse.Initialization.request(**options)

        self._convert_from_parse(response)
        # todo decode response


    def delete(self):
        raise NotImplemented

    def _convert_from_parse(self, response):
        for k,v in response.items():
            setattr(self, k, v)

        self._is_dirty = False

    def __setattr__(self, key, value):
        if key in self.__class__.meta:
            super(ParseObject, self).__setattr__(key, value)
        else:
            self._data[key] = value

    def __getattr__(self, item):
        return self._data[item]

    @classmethod
    def extend(cls, class_name):
        if class_name == 'User':
            raise NotImplemented

        # cannot extend two degrees away from ParseObject
        if cls != ParseObject:
            raise Exception

        new_class = type(class_name, (ParseObject,), {})
        ParseObject.class_map[class_name] = new_class

        return new_class

    @classmethod
    def get(cls, objectId):
        options = {
            'route': 'classes',
            'class_name': cls.__name__,
            'method': 'GET',
            'objectId': objectId
        }

        response = Parse.Initialization.request(**options)
        c = cls()
        c._convert_from_parse(response)
        return c

