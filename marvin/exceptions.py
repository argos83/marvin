"""Marvin's Exceptions"""


class StepShouldSkip(Exception):
    """
    This exception is raised when a step is flagged to be skipped
    """
    def __init__(self, message):
        Exception.__init__(self, message)
