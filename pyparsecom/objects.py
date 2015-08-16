from .core import Parse
from .exceptions import ParseClassDoesNotExist, ParseResourceException
from six import add_metaclass


class ComplexTypeMeta(type):
    register = {}

    def __new__(mcs, name, bases, class_dict):
        if name not in mcs.register:
            cls = type.__new__(mcs, name, bases, class_dict)
            mcs.register[name] = cls
        return mcs.register[name]


@add_metaclass(ComplexTypeMeta)
class ParseType(object):
    PROTECTED_ATTRIBUTES = ['_dirty_keys', '_is_loaded', 'objectId', 'createdAt',
                            'updatedAt', '__type', 'className']

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _convert_from_native_to_parse(self):
        pass


class ParseObject(ParseType):
    def __init__(self, **kwargs):
        self._dirty_keys = set([])
        self._is_loaded = False

        super(ParseObject, self).__init__(**kwargs)

        if not hasattr(self, 'className'):
            self.className = self.__class__.__name__

    def __setattr__(self, key, value):
        if key not in self.__class__.PROTECTED_ATTRIBUTES:
            self._dirty_keys.add(key)

        super(ParseObject, self).__setattr__(key, value)

    def fetch(self):
        if not hasattr(self, 'objectId'):
            raise ParseResourceException('no objectId')  # cannot fetch without id

        options = {
            'route': 'classes',
            'className': self.__class__.__name__,
            'method': 'GET',
            'objectId': self.objectId
        }

        response = Parse.Initialization.request(**options)

        self._load_from_parse(response)

        self._is_loaded = True
        self._dirty_keys.clear()

    def save(self):
        options = {
            'route': 'classes',
            'className': self.__class__.__name__,
            'method': 'POST',
            'data': dict((k, v) for k, v in self._convert_from_native_to_parse().items() if k in self._dirty_keys)
        }

        if hasattr(self, 'objectId'):
            options['method'] = 'PUT'
            options['objectId'] = self.objectId

        response = Parse.Initialization.request(**options)
        self._load_from_parse(response)
        self._dirty_keys.clear()

    def delete(self):
        options = {
            'route': 'classes',
            'className': self.className,
            'objectId': self.objectId,
            'method': 'DELETE'
        }

        Parse.Initialization.request(**options)

    def _load_from_parse(self, response):
        for k, v in response.items():
            setattr(self, k, self.__class__._convert_from_parse_to_native(k, v))

    @classmethod
    def get(cls, objectId):
        options = {
            'route': 'classes',
            'className': cls.__name__,
            'method': 'GET',
            'objectId': objectId
        }

        response = Parse.Initialization.request(**options)
        c = cls()
        c._load_from_parse(response)
        return c

    def _convert_from_native_to_parse(self):
        data = {}

        for k, v in self.__dict__.items():
            if k in ParseType.PROTECTED_ATTRIBUTES or k not in self._dirty_keys:
                continue

            if isinstance(v, ParseObject):
                data[k] = v.to_pointer()._convert_from_native_to_parse()
            elif isinstance(v, ParseType):
                data[k] = v._convert_from_native_to_parse()
            else:
                data[k] = v

        return data

    @staticmethod
    def _convert_from_parse_to_native(key, data):
        if not isinstance(data, dict):
            return data

        parse_type = None

        if '__type' in data:
            parse_type = str(data.pop('__type'))
        elif key == 'ACL':
            parse_type = 'ACL'

        cls = ComplexTypeMeta.register.get(parse_type, None)

        if cls is None:
            raise ParseClassDoesNotExist('%s does not exist', parse_type)

        complex_object = type(parse_type, (cls,), data)

        return complex_object

    def to_pointer(self):
        if not hasattr(self, 'objectId'):
            self.save()

        cls = ComplexTypeMeta.register.get('Pointer', None)

        if cls is None:
            raise ParseClassDoesNotExist('Pointer does not exist')

        return type('Pointer', (cls,), {})(className=self.className,
                                           objectId=self.objectId)

