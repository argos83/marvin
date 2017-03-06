from marvin.report import Publisher


class Context(object):

    def __init__(self, parent_context=None):
        self._ctx = parent_context
        self._publisher = self.ctx.publisher if self.ctx else Publisher()

    @property
    def ctx(self):
        return self._ctx

    @property
    def publisher(self):
        return self._publisher
