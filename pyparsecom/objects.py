from .core import Parse


class ComplexTypeMeta(type):
    register = {}

    def __new__(mcs, name, bases, class_dict):
        if name not in mcs.register:
            cls = type.__new__(mcs, name, bases, class_dict)
            mcs.register[name] = cls
        return mcs.register[name]


class ParseType(object):
    __metaclass__ = ComplexTypeMeta
    meta_fields = ['_data', '_is_dirty', '_is_loaded', 'objectId', 'createdAt', 'updatedAt', '__type']

    @staticmethod
    def convert_from_parse_to_native(key, data):
        if not isinstance(data, dict):
            return data

        parse_type = None

        if '__type' in data:
            parse_type = str(data.pop('__type'))
        elif key == 'ACL':
            parse_type = 'ACL'

        cls = ComplexTypeMeta.register.get(parse_type, None)

        if cls is None:
            raise Exception

        complex_object = type(parse_type, (cls,), data)

        return complex_object

    def convert_from_native_to_parse(self):
        data = {}

        for k, v in self.__dict__.items():
            if k in ParseType.meta_fields:
                continue

            data[k] = v

        return data


class ParseObject(ParseType):

    def __init__(self, **kwargs):
        self._is_dirty = True
        self._is_loaded = False
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

        self._load_from_parse(response)

        self._is_loaded = True
        self._is_dirty = False

    def save(self):
        options = {
            'route': 'classes',
            'class_name': self.__class__.__name__,
            'method': 'POST',
            'data': self.convert_from_native_to_parse()
        }

        if hasattr(self, 'objectId'):
            options['method'] = 'PUT'
            options['objectId'] = self.objectId

        response = Parse.Initialization.request(**options)
        self._load_from_parse(response)

        self._is_dirty = False

    def delete(self):
        raise NotImplemented

    def _load_from_parse(self, response):
        for k,v in response.items():
            setattr(self, k, ParseType.convert_from_parse_to_native(k, v))


    @classmethod
    def extend(cls, class_name):
        if class_name == 'User':
            raise NotImplemented

        # cannot extend two degrees away from ParseObject
        if cls != ParseObject:
            raise Exception

        if class_name in Parse.class_map:
            return Parse.class_map[class_name]

        new_class = type(class_name, (ParseObject,), {})
        Parse.class_map[class_name] = new_class

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
        c._load_from_parse(response)
        return c


class GeoPoint(ParseType):
    __name__ = 'GeoPoint'