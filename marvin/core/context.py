from marvin.core.status import Status
from marvin.exceptions import ContextSkippedException
from marvin.report import Publisher


class Context(object):

    def __init__(self, parent_context=None):
        self._ctx = parent_context
        self._publisher = self.ctx.publisher if self.ctx else Publisher()
        self._sub_context_results = {
            Status.PASS: 0,
            Status.FAIL: 0,
            Status.SKIP: 0
        }

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
        """Keep count of sub-context results within this context"""
        self._sub_context_results[status] += 1
