from marvin.core.reportable import Reportable


def test_reportable_default_settings():
    """Verify default reportable properties"""

    class SomeReportableEntity(Reportable):
        pass

    rep = SomeReportableEntity()

    assert rep.name == 'SomeReportableEntity'
    assert rep.description == 'No description'
    assert rep.tags == set()


def test_reportable_description_from_docstring():
    """Reportable description can be set from class docstring"""

    class SomeReportableEntity(Reportable):
        """
        With a cool description
        """

    rep = SomeReportableEntity()
    assert rep.description == 'With a cool description'


def test_reportable_details_override():
    """Explicit NAME and DESCRIPTION are prioritized over class name and docstring"""

    class SomeReportableEntity(Reportable):
        """This won't be the description"""
        DESCRIPTION = "But this will"
        NAME = "A different name"
        TAGS = ['and', 'some', 'tags']

    rep = SomeReportableEntity()
    assert rep.description == 'But this will'
    assert rep.name == 'A different name'
    assert rep.tags == set(['and', 'some', 'tags'])


def test_reportable_dynamic_tagging_untagging():
    """Intances support dynamic tagging and untagging of instance and class tags"""
    class SomeReportableEntity(Reportable):
        TAGS = ['some', 'tags']

    rep = SomeReportableEntity()
    rep.tag('and', 'a', 'few', 'labels')
    rep.untag('some', 'other')
    assert rep.tags == set(['tags', 'and', 'a', 'few', 'labels'])


def test_reportable_inherited_tags():
    """Tags from super reportable classes are automatically inherited"""

    class GenericReportableEntity(Reportable):
        TAGS = ['generic1', 'generic2']

    class MoreSpecificReportableEntity(GenericReportableEntity):
        TAGS = ['specific1', 'remove_me']

    class UltraSpecificReportableEntity(MoreSpecificReportableEntity):
        TAGS = ['very_specific1']

    rep = UltraSpecificReportableEntity()
    rep.tag('keep_me', 'remove_me_too')
    rep.untag('remove_me', 'remove_me_too')

    assert rep.tags == set(['generic1', 'generic2', 'specific1', 'very_specific1', 'keep_me'])
