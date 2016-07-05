from plone.dexterity.content import Container
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides


class IDummySchema(form.Schema):
    """Dummy schema used for testing.
    """

    int_field = schema.Int(
        title=u'Int Field',
        required=False,
        default=111,
    )


class IDummyAttributeStorageBehavior(form.Schema):

    attr_behavior_int_field = schema.Int(
        title=u'Behavior (AttributeStorage) Int Field',
        required=False,
        default=222,
    )

alsoProvides(IDummyAttributeStorageBehavior, form.IFormFieldProvider)


class IDummyAnnotationStorageBehavior(form.Schema):

    ann_behavior_int_field = schema.Int(
        title=u'Behavior (AnnotationStorage) Int Field',
        required=False,
        default=333,
    )

alsoProvides(IDummyAnnotationStorageBehavior, form.IFormFieldProvider)


class Dummy(Container):
    """Dummy type used for testing"""
