class BaseAuthSystemError(Exception):
    pass


class InvalidAuthDataError(BaseAuthSystemError):
    pass


class OperationForbiddenError(BaseAuthSystemError):
    pass
