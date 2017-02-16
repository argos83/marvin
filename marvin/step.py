import time
import sys

from marvin.report.publisher import Publisher, Events

class Step(object):
    """Marvin's Step class"""

    def __init__(self):
        self._runtime_tags = []
        self._expected_exception = None
        self._do_after = None

    def expecting_exception(self, arg):
        """
        Fluent interface:
        Specifies an exception expectation: The argument can be either:
            * An expected exception class
            * A list of possible expected exception classes
            * A function (e.g. lambda) which receives an exception object. If the result
                evaluates as True, the exception was expected.
        """
        self._expected_exception = arg
        return self

    def doing_after(self, block):
        """
        Fluent interface:
        Executes the given function right after the step's run method.
        The function will be invoked passing the step instance and whatever the run method returns.
        E.g.:

        CreateOrderStep().doing_after(
                lambda step, order: assert order.status == 'complete'
            ).execute()
        """
        self._do_after = block
        return self

    @property
    def name(self):
        return getattr(self.__class__, "NAME", self.__class__.__name__)

    @property
    def description(self):
        return getattr(self.__class__, "DESCRIPTION", "")

    @property
    def tags(self):
        """
        Returns the Step's tags, which include:
         * All the tags defined at runtime in the step instance (tag method)
         * All the tags defined in the step class ('TAGS' attribute)
         * All the tags defined in this step's superclasses
        """
        return self._runtime_tags + self.__class__._class_tags()
       
    def tag(self, *tags):
        """
        Add one or more tags to the step's instance dinamically
        E.g.:  the_step.tag("wip", "regression")
        """
        self._runtime_tags.extend(tags)

    def execute(self, *args, **kargs):
        """Main step executor"""

        start = int(time.time() * 1000)
        data = {"step": self,
                "args": args,
                "kargs": kargs,
                "timestamp": start}

        Publisher.notify(Events.STEP_STARTED, data)

        result, status, exc_info = self._execute(*args, **kargs)

        data = {"step": self,
                "result": result,
                "status": status,
                "start_time": start,
                "exception": exc_info,
                "timestamp": int(time.time() * 1000)}
        Publisher.notify(Events.STEP_ENDED, data)

        if exc_info and status == "FAILED":
            raise exc_info[0], exc_info[1], exc_info[2]

        return result

    def run(self, *args, **kargs):
        """Step's logic implementation (to be redefined by sub-classes)"""
        raise NotImplementedError("Method run must be redefined")

    # Private methods

    def _execute(self, *args, **kargs):
        status = "PASSED"
        exc_info = None
        result = None

        try:
            result = self.run(*args, **kargs)
            if (self._do_after):
                self._do_after(self, result)
        except:
            exc_info = sys.exc_info()
            
        if self._should_fail(exc_info):
            status = "FAILED"

        return result, status, exc_info

    def _should_fail(self, exc_info):
        # No exception was raised but one was expected
        if not exc_info and self._expected_exception:
            return True

        # No exception raised nor expected
        elif not exc_info:
            return False

        # There was an exception but it was not expected
        if exc_info and not self._expected_exception:
            return True

        return self.exc_info[0] != exception.__class__

    @classmethod
    def _class_tags(cls):
        # Retrieve tags defined at a class level (if any)
        return cls._base_tags() + getattr(cls, 'TAGS', [])

    @classmethod
    def _base_tags(cls):
        # Retrieve the tags from the super-classes recursively
        tags = []
        for klass in cls.__bases__:
            if issubclass(klass, Step) and klass != Step:
                tags += klass._class_tags()
        return tags