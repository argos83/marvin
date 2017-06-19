
class Reportable(object):
    """
    Mix-In class for all those Marvin entities that are considered to be 'reportable'
    E.g. Steps, TestScripts, and Suites
    It adds capabilities to define name, description, and tags properties
    """

    def __init__(self):
        self._runtime_tags = set()
        self._removed_tags = set()
        self._name = getattr(self, 'NAME', self.__class__.__name__)
        self._description = getattr(self, 'DESCRIPTION', self._default_description())

    @property
    def name(self):
        """Name property for this instance"""
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = str(new_name)

    @property
    def description(self):
        """Description property for this instance"""
        return self._description

    @description.setter
    def description(self, new_description):
        self._description = str(new_description)

    @property
    def tags(self):
        """Retrieve the full set of tags for this instance (class and instance tags)"""
        hierarchy_tags = self.class_tags()
        return (self._runtime_tags | hierarchy_tags) - self._removed_tags

    def tag(self, *tags):
        """Dynamically add tags to this instance"""
        self._runtime_tags |= set(str(tag) for tag in tags)

    def untag(self, *tags):
        """Remove tags (instance or class) for this instance"""
        self._removed_tags |= set(str(tag) for tag in tags)

    @classmethod
    def class_tags(cls):
        """Retrieve all the tags of this class and its superclasses"""
        tags = set(getattr(cls, 'TAGS', []))
        for base_class in cls.__bases__:
            if issubclass(base_class, Reportable) and base_class != Reportable:
                tags |= base_class.class_tags()
                break
        return tags

    def _default_description(self):
        if self.__class__.__doc__:
            return self.__class__.__doc__.strip()
        return 'No description'
