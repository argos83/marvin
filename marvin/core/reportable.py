
class Reportable(object):

    def __init__(self):
        self._runtime_tags = set()
        self._removed_tags = set()

    @property
    def description(self):
        default = "No description"
        if self.__class__.__doc__:
            default = self.__class__.__doc__.strip()

        return getattr(self, 'DESCRIPTION', default)

    @property
    def name(self):
        return getattr(self, 'NAME', self.__class__.__name__)

    @property
    def tags(self):
        class_tags = set(getattr(self, 'TAGS', []))
        parent_tags = set()  # TODO: retrieve tags from superclasses

        return (self._runtime_tags | class_tags | parent_tags) - self._removed_tags

    def tag(self, *tags):
        self._runtime_tags |= set(tags)

    def untag(self, *tags):
        self._removed_tags |= set(tags)
