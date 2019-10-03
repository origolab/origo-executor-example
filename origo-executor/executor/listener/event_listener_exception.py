class EventListenerException(Exception):
    """
    Base class for Executor Worker Exceptions.
    """
    pass


class SetupException(EventListenerException):
    """
    Failed to setup data.
    """
    pass


class FileDownloadException(SetupException):
    """
    Failed to download data.
    """
    pass


class CheckSumException(SetupException):
    """
    Failed to check the hash matches.
    """
    pass

