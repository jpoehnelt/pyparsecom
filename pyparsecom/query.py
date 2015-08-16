import pyparsecom


class Query(object):
    def __init__(self, className):
        self.className = className

    def count(self):
        return 0

    def fetch(self):
        options = {
            'route': 'classes',
            'className': self.className,
            'method': 'GET'
        }

        response = pyparsecom.core.Parse.Initialization.request(**options)

        for row in response['results']:
            cls = pyparsecom.objects.ComplexTypeMeta.register.get(self.className, None)

            if cls is None:
                raise pyparsecom.exceptions.ParseClassDoesNotExist('%s does not exist' % self.className)

            item = type(self.className, (cls,), {})()
            pyparsecom.objects.ParseObject.load_from_parse(row, item=item, is_loaded=True)

            yield item

    def filter(self):
        return self

    def get(self, objectId):
        options = {
            'route': 'classes',
            'className': self.className,
            'objectId': objectId,
            'method': 'GET'
        }

        response = pyparsecom.core.Parse.Initialization.request(**options)

        cls = pyparsecom.objects.ComplexTypeMeta.register.get(self.className, None)

        if cls is None:
            raise pyparsecom.exceptions.ParseClassDoesNotExist('%s does not exist' % self.className)

        item = type(self.className, (cls,), {})()
        pyparsecom.objects.ParseObject.load_from_parse(response, item=item, is_loaded=True)

        return item

    def include(self, attribute):
        return self

    def keys(self):
        return self

    def limit(self):
        return self

    def order(self, attribute):
        return self

    def skip(self):
        return self
