class BaseCustomError(Exception):
    MESSAGE = None
    def __init__(self):
        super().__init__()
        self.message = self.MESSAGE

class NoValidStatusCode(BaseCustomError):
    MESSAGE = 'Status code not equal 200'

class NoValidStatusHomework(BaseCustomError):
    MESSAGE = 'Status homework no valid'

class NoNameHomework(BaseCustomError):
    MESSAGE = 'Missing homework_name'


class NoRequiredKey(BaseCustomError):
    MESSAGE = 'No required key'


class ApiConnectionError(BaseCustomError):
    MESSAGE = 'API connection error'
