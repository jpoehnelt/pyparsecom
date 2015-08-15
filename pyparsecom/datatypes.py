from core import Parse


class ParseObject(object):
    meta = ['_data', '_is_synced']
    class_map = {}

    def __init__(self):
        self._is_synced = False
        self._data = {}

    def fetch(self):
        raise NotImplemented

    def save(self):
        raise NotImplemented

    def delete(self):
        raise NotImplemented

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

