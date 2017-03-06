
class Reportable(object):
    """
    Mix-In class for all those Marvin entities that are considered to be 'reportable'
    E.g. Steps, TestScripts, and Suites
    It adds capabilities to define name, description, and tags properties
    """

    def __init__(self):
        self._runtime_tags = set()
        self._removed_tags = set()

    @property
    def description(self):
        """Description property for this instance"""
        default = "No description"
        if self.__class__.__doc__:
            default = self.__class__.__doc__.strip()

        return getattr(self, 'DESCRIPTION', default)

    @property
    def name(self):
        """Name property for this instance"""
        return getattr(self, 'NAME', self.__class__.__name__)

    @property
    def tags(self):
        """Retrieve the full set of tags for this instance (class and instance tags)"""
        hierarchy_tags = self.class_tags()
        return (self._runtime_tags | hierarchy_tags) - self._removed_tags

    def tag(self, *tags):
        """Dynamically add tags to this instance"""
        self._runtime_tags |= set(tags)

    def untag(self, *tags):
        """Remove tags (instance or class) for this instance"""
        self._removed_tags |= set(tags)

    @classmethod
    def class_tags(cls):
        """Retrieve all the tags of this class and its superclasses"""
        tags = set(getattr(cls, 'TAGS', []))
        for base_class in cls.__bases__:
            if issubclass(base_class, Reportable) and base_class != Reportable:
                tags |= base_class.class_tags()
                break
        return tags
