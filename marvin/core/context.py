from marvin.exceptions import ContextSkippedException
from marvin.report import Publisher


class Context(object):

    def __init__(self, parent_context=None):
        self._ctx = parent_context
        self._publisher = self.ctx.publisher if self.ctx else Publisher()

    @property
    def ctx(self):
        """This context's context (i.e. the parent context)"""
        return self._ctx

    @property
    def publisher(self):
        """The publisher instance for this context"""
        return self._publisher

    def skip(self, reason=None):
        """Trigger a signal for this context execution to be skipped"""
        raise ContextSkippedException(self, reason=reason)

    @property
    def level(self):
        """Depth level of this context (i.e. how many ancestors contexts it has)"""
        if not self._ctx:
            return 0
        return self._ctx.level + 1

    def sub_context_finished(self, status):
        """
        Context implementations can decide what
        to do when a sub-context has finished with a specific status
        """
        pass
