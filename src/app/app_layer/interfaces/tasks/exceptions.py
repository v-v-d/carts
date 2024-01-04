class TaskProducerError(Exception):
    pass


class TaskProducerInitializationError(TaskProducerError):
    pass


class TaskProducingError(TaskProducerError):
    pass


class TaskIsNotQueuedError(TaskProducerError):
    pass
