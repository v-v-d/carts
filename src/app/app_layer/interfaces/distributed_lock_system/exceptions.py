class BaseDistributedLockSystemError(Exception):
    pass


class AlreadyLockedError(BaseDistributedLockSystemError):
    pass
