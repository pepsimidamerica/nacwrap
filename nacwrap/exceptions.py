"""
Module contains any custom exceptions.
"""


class WorkflowApiError(Exception):
    """
    Represents some generic error that has come up while accessing the Nintex API.

    :param message: Description of the error.
    :type message: str
    :param status_code: HTTP status code of the failed response, if there was one.
    :type status_code: int | None
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """
        Store the message and optional HTTP status code.

        :param message: Description of the error.
        :type message: str
        :param status_code: HTTP status code of the failed response, if there was one.
        :type status_code: int | None
        """
        super().__init__(message)
        self.status_code = status_code
