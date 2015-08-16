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

from six import add_metaclass
from .core import Parse
from .exceptions import ParseClassDoesNotExist, ParseResourceException


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
                            'updatedAt', '__type', 'className', '_parents']

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        super(ParseType, self).__setattr__(key, value)
        self._mark_parent_dirty()

    def __delattr__(self, key):
        super(ParseType, self).__delattr__(key)
        self._mark_parent_dirty()

    def _convert_from_native_to_parse(self):
        pass

    def add_parent(self, parent, attribute):

        # parse objects only store pointers
        if isinstance(self, ParseObject):
            return

        if not hasattr(self, '_parents'):
            self._parents = {}

        if parent not in self._parents:
            self._parents[parent] = attribute

    def remove_parent(self, parent):
        if parent in self._parents:
            del self._parents[parent]

    def _mark_parent_dirty(self):
        """
        This marks all of the parents referencing this complex type as dirty.
        :return:
        """
        if hasattr(self, '_parents'):
            for parent in self._parents.keys():
                attribute = self._parents[parent]
                if attribute in self.__class__.PROTECTED_ATTRIBUTES:
                    continue

                if getattr(parent, attribute) != self:
                    self.remove_parent(parent)
                    continue

                parent._dirty_keys.add(attribute)


class ParseObject(ParseType):
    def __init__(self, **kwargs):
        self._dirty_keys = set([])
        self._is_loaded = False

        super(ParseObject, self).__init__(**kwargs)

        if not hasattr(self, 'className'):
            self.className = self.__class__.__name__

    def __setattr__(self, key, value):
        """
        If attribute is changed set the parent of the complex type and remove from
        previous complex type if necessary.
        :param key: attribute name
        :param value: attribute value
        :return:
        """
        if key not in self.__class__.PROTECTED_ATTRIBUTES:
            self._dirty_keys.add(key)

        if isinstance(getattr(self, key, None), ParseType):
            getattr(self, key).remove_parent(self)

        if isinstance(value, ParseType):
            value.add_parent(parent=self, attribute=key)

        super(ParseObject, self).__setattr__(key, value)

    def __delattr__(self, key):
        """
        Remove the parent reference from the complex type.
        :param key: attribute name
        :return:
        """
        if key not in self.__class__.PROTECTED_ATTRIBUTES:
            self._dirty_keys.add(key)

            if isinstance(getattr(self, key, None), ParseType):
                getattr(self, key).remove_parent(self)

            super(ParseObject, self).__delattr__(key)

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

        ParseObject.convert_from_parse_to_native(response, item=self, is_loaded=True)

    def save(self):
        """
        Saves all dirty attributes of the object to Parse. After, dirty keys are cleared. However
        Parse does not return the other attributes and therefore the object is not marked as loaded.
        :return:
        """
        options = {
            'route': 'classes',
            'className': self.__class__.__name__,
            'method': 'POST',
            'data': dict((k, v) for k, v in self._convert_from_native_to_parse().items() if
                         k in self._dirty_keys)
        }

        if hasattr(self, 'objectId'):
            options['method'] = 'PUT'
            options['objectId'] = self.objectId

        response = Parse.Initialization.request(**options)
        ParseObject.convert_from_parse_to_native(response, item=self, is_loaded=False)
        self._dirty_keys.clear()

    def delete(self):
        """
        Delete the object from Parse. It still exists locally.
        :return:
        """
        options = {
            'route': 'classes',
            'className': self.className,
            'objectId': self.objectId,
            'method': 'DELETE'
        }

        Parse.Initialization.request(**options)

    @staticmethod
    def convert_from_parse_to_native(response, className=None, item=None, is_loaded=True):

        if item is None:
            cls = ComplexTypeMeta.register.get(className, None)

            if cls is None:
                raise ParseClassDoesNotExist('%s does not exist' % className)

            item = type(className, (cls,), {})()

        for k, v in response.items():
            setattr(item, k, item._convert_attribute_from_parse_to_native(k, v))

            if k in item._dirty_keys:
                item._dirty_keys.remove(k)

        item._is_loaded = is_loaded

        return item

    def _convert_from_native_to_parse(self):
        data = {}

        for k, v in self.__dict__.items():
            if isinstance(v, ParseObject):
                data[k] = v.to_pointer()._convert_from_native_to_parse()
            elif isinstance(v, ParseType):
                data[k] = v._convert_from_native_to_parse()
            else:
                data[k] = v

        return data

    def _convert_attribute_from_parse_to_native(self, key, data):
        """
        Converts attributes to python class by examining the data of the attribute.
        :param key: attribute name
        :param data: attribute data
        :return:
        """

        # cast to data if possible
        try:
            data = pyparsecom.types.Date.from_str(data)
        except Exception as e:
            pass
        else:
            return data

        # if not a dict it cannot be a complex type
        if not isinstance(data, dict):
            return data

        # get the complex type
        if '__type' in data:
            parse_type = str(data.pop('__type'))
        elif key == 'ACL':
            parse_type = 'ACL'
        else:
            return data

        # get the python class for the typ
        cls = ComplexTypeMeta.register.get(parse_type, None)

        if cls is None:
            raise ParseClassDoesNotExist('%s does not exist', parse_type)

        # instantiate the object
        item = type(parse_type, (cls,), {})(**data)

        # add parent to the object so that when this object is updated, the parent is marked as
        # dirty
        item.add_parent(parent=self, attribute=key)

        return item

    def to_pointer(self):
        if not hasattr(self, 'objectId'):
            self.save()

        cls = ComplexTypeMeta.register.get('Pointer', None)

        if cls is None:
            raise ParseClassDoesNotExist('Pointer does not exist')

        return type('Pointer', (cls,), {})(className=self.className,
                                           objectId=self.objectId)


# register types
import pyparsecom.types
import pyparsecom.user