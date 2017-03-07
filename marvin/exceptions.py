"""Marvin's Exceptions"""


class MarvinException(Exception):
    """Base exception for all marvin's exceptions"""
    def __init__(self, message=None):
        message = message or "An exception was raised in Marvin"
        super(MarvinException, self).__init__(message)


class ContextSkippedException(MarvinException):
    """Raised when a context entity (e.g. Step, TestScript, or Suite) is flagged to be skipped"""
    def __init__(self, context, reason=None):
        self.reason = reason or "Step skipped"
        self.context = context
        super(ContextSkippedException, self).__init__(self.reason)


class ExpectedExceptionNotRaised(MarvinException):
    """Raised when a step has defined exception expectations but nothing was raised"""
    def __init__(self, expectations):
        self.expectations = expectations
        expecting = expectations[0] if len(expectations) == 1 else expectations
        message = "No exception was raised, but the expectation was: %s" % expecting
        super(ExpectedExceptionNotRaised, self).__init__(message)
