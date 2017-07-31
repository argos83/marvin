from marvin.data import IterationData

from tests.stubs.exception import FakeTraceback, FakeFrame, FakeCode


class IterationDataBuilder(object):
    def __init__(self):
        self._args = {}

    def with_data(self, **kwargs):
        self._args['data'] = kwargs
        return self

    def with_name(self, name):
        self._args['name'] = name
        return self

    def with_description(self, description):
        self._args['description'] = description
        return self

    def with_tags(self, *args):
        self._args['tags'] = args
        return self

    def build(self):
        return IterationData(**self._args)


class TracebackBuilder(object):
    def __init__(self, frames=None):
        self._frames = frames or []

    def with_frame(self, filename, line, line_no):
        frame = {'filename': filename, 'line': line, 'line_no': line_no}
        frames = self._frames[:]
        frames.append(frame)
        return TracebackBuilder(frames)

    def build(self):
        frames = []
        line_nos = []
        for entry in self._frames:
            code = FakeCode(entry['filename'], entry['line'])
            frame = FakeFrame(code, {})
            frames.append(frame)
            line_nos.append(entry['line_no'])
        return FakeTraceback(frames, line_nos)
