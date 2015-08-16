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
import json
from copy import deepcopy
from .core import Parse
from .objects import ParseObject, ComplexTypeMeta
from .exceptions import ParseClassDoesNotExist


class Query(object):

    def __init__(self, className):
        self.className = className
        self.params = {
            'where': {},
            'order': []
        }

    def build(self):
        params = deepcopy(self.params)
        params['where'] = json.dumps(params['where'])

        if len(params['order']) == 0:
            del params['order']
        else:
            params['order'] = ','.join(params['order'])

        if 'keys' in params:
            params['keys'] = ','.join(params['keys'])

        return urlencode(params)

    def count(self):
        pass

    def fetch(self):
        options = {
            'route': 'classes',
            'className': self.className,
            'method': 'GET',
            'params': self.build()
        }
        print(options)
        response = Parse.Initialization.request(**options)

        # not calling it loaded if keys were specified
        is_loaded = 'keys' not in self.params or self.params['keys'] == 1

        return QuerySet(results=response['results'], className=self.className, is_loaded=is_loaded)

    def get(self, objectId):
        options = {
            'route': 'classes',
            'className': self.className,
            'objectId': objectId,
            'method': 'GET'
        }

        response = Parse.Initialization.request(**options)

        cls = ComplexTypeMeta.register.get(self.className, None)

        if cls is None:
            raise ParseClassDoesNotExist('%s does not exist' % self.className)

        item = type(self.className, (cls,), {})()
        ParseObject.convert_from_parse_to_native(response, item=item, is_loaded=True)

        return item

    def include(self, attribute):
        q = deepcopy(self)
        return q

    def keys(self, keys):
        q = deepcopy(self)
        q.params['keys'] = keys
        return q

    def first(self):
        q = deepcopy(self)
        q.skip(0)
        q.limit(1)
        return q

    def limit(self, n):
        q = deepcopy(self)
        q.params['limit'] = n
        return q

    def skip(self, n):
        q = deepcopy(self)
        q.params['skip'] = n
        return q

    def ascending(self, attribute):
        q = deepcopy(self)
        q.params['order'].append(attribute)
        return q

    def descending(self, attribute):
        q = deepcopy(self)
        q.params['order'].append('-' + attribute)
        return q

    # filters

    def equal_to(self, attribute, value):
        q = deepcopy(self)
        if attribute in q.params['where']:
            raise Exception
        q.params['where'][attribute] = value
        return q

    def not_equal_to(self, attribute, value):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$ne'] = value
        return q

    def greater_than(self, attribute, value):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$gt'] = value
        return q

    def greater_than_or_equal(self, attribute, value):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$gte'] = value
        return q

    def less_than(self, attribute, value):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$lt'] = value
        return q

    def less_than_or_equal(self, attribute, value):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$lte'] = value

        return q

    def contained_in(self, attribute, values):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$in'] = values
        return q

    def not_contained_in(self, attribute, values):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$nin'] = values
        return q

    def exists(self, attribute):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$exists'] = True
        return q

    def does_not_exist(self, attribute):
        q = deepcopy(self)
        if attribute not in q.params['where']:
            q.params['where'][attribute] = {}
        q.params['where'][attribute]['$exists'] = False
        return q


class QuerySet(object):

    def __init__(self, results, className, is_loaded=True):
        self.results = results
        self.className = className
        self.is_loaded = is_loaded

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        for row in self.results:
            cls = ComplexTypeMeta.register.get(self.className, None)

            if cls is None:
                raise  ParseClassDoesNotExist(
                    '%s does not exist' % self.className)

            item = type(self.className, (cls,), {})()
            ParseObject.convert_from_parse_to_native(row, item=item, is_loaded=self.is_loaded)

            yield item

