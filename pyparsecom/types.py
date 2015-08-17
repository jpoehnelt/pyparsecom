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

import datetime
import six
import base64
from .objects import ParseType, ComplexTypeMeta
from .exceptions import ParseClassDoesNotExist


class GeoPoint(ParseType):
    __name__ = 'GeoPoint'

    def __eq__(self, other):
        return self.latitude == other.latitude and self.longitude == other.longitude

    def _convert_from_native_to_parse(self):
        return {
            '__type': 'GeoPoint',
            'latitude': self.latitude,
            'longitude': self.longitude
        }


class Pointer(ParseType):
    __name__ = 'Pointer'

    def convert_from_native_to_parse(self):
        return {
            '__type': 'Pointer',
            'className': self.className,
            'objectId': self.objectId
        }

    def load(self):
        cls = ComplexTypeMeta.register.get(self.className, None)

        if cls is None:
            raise ParseClassDoesNotExist('%s does not exist' % self.className)

        return type(self.className, (cls,), {})(**self.__dict__)


class Date(ParseType):
    FORMAT = '%Y-%m-%dT%H:%M:%S.%f%Z'

    @staticmethod
    def from_str(date_str):
        """turn a ISO 8601 string into a datetime object"""
        return datetime.datetime.strptime(date_str[:-1] + 'UTC', Date.FORMAT)

    def __init__(self, date):
        """Can be initialized either with a string or a datetime"""
        if isinstance(date, datetime.datetime):
            self._date = date
        elif isinstance(date, six.string_types):
            self._date = Date.from_str(date)

        super(Date, self).__init__()

    def _convert_from_native_to_parse(self):
        # parse expects an iso8601 with 3 digits milliseonds and not 6
        return {
            '__type': 'Date',
            'iso': '{0}Z'.format(self._date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])
        }


class Binary(ParseType):
    def __init__(self, encoded_string):
        self._encoded = encoded_string
        self._decoded = str(base64.b64decode(self._encoded))
        super(Binary, self).__init__()

    def _convert_from_native_to_parse(self):
        return {'__type': 'Bytes', 'base64': self._encoded}

