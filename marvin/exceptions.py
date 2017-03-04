"""Marvin's Exceptions"""


class MarvinException(Exception):
    """Base exception for all marvin's exceptions"""
    def __init__(self, message=None):
        if message is None:
            message = "An exception was raised in Marvin"

        super(MarvinException, self).__init__(message)


class StepSkipped(MarvinException):
    """This exception is raised when a step is flagged to be skipped"""
    def __init__(self, message=None):
        if message is None:
            message = "Step skipped"
        super(StepSkipped, self).__init__(message)
