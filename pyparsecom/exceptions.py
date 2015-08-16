class ParseError(Exception):
    def __init__(self, **kwargs):
        self.code = kwargs.get('code')
        self.error = kwargs.get('error')

        message = '%s %d' % (self.error, self.code)

        super(ParseError, self).__init__(message)

class ParseResourceException(Exception):
    pass

class ParseClassDoesNotExist(Exception):
    pass

