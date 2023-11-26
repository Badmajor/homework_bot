class NoValidStatusCode(Exception):
    def __init__(self, message='Status code not equal 200'):
        super().__init__()
        self.message = message


class NoValidStatusHomework(Exception):
    def __init__(self, message='Status homework no valid'):
        super().__init__()
        self.message = message


class NoNameHomework(Exception):
    def __init__(self, message='Missing homework_name'):
        super().__init__()
        self.message = message


class NoRequiredKey(Exception):
    def __init__(self, message='No required key'):
        super().__init__()
        self.message = message


class TokensError(Exception):
    def __init__(self, token=None, message='Missing token'):
        super().__init__()
        self.token = token
        self.message = message

    def __str__(self):
        return f'{self.message}: {self.token}'