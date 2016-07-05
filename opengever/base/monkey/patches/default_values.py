from copy import deepcopy
from opengever.base.monkey.patching import MonkeyPatch
from plone.dexterity.content import _marker
from zope.schema.interfaces import IContextAwareDefaultFactory


def _default_from_schema(context, schema, fieldname):
    """Helper to look up default value of a field

    (taken from plone.dexterity.utils 2.3.0 )
    """
    if schema is None:
        return _marker
    field = schema.get(fieldname, None)
    if field is None:
        return _marker
    if IContextAwareDefaultFactory.providedBy(
            getattr(field, 'defaultFactory', None)
    ):
        bound = field.bind(context)
        return deepcopy(bound.default)
    else:
        return deepcopy(field.default)
    return _marker


class PatchDexterityContentGetattr(MonkeyPatch):
    """Patch DexterityContent.__getattr__ to correctly fall back to defaults
    from behavior schemas with *marker* interfaces.

    Rationale: The implementation in plone.dexterity 2.1.x grabs
    *marker interfaces* from SCHEMA_CACHE.subtypes() for behaviors that have
    them, instead of their schema interfaces.

    If there's a fallback logic in place (and we can't get rid of
    it), it should at least work consistently.

    The __getattr__ below is an exact copy of DexterityContent.__getattr__
    from plone.dexterity == 2.3.0. That version doesn't use SCHEMA_CACHE at
    all for behavior schemata, and so avoids using the questionable
    SCHEMA_CACHE.subtypes(). This was fixed in plone/plone.dexterity#21 by
    @jensens as part of a major overhaul / unification of behavior lookups.
    """

    def __call__(self):
        from plone.behavior.interfaces import IBehaviorAssignable
        from plone.dexterity.schema import SCHEMA_CACHE

        def __getattr__(self, name):
            # python basics:  __getattr__ is only invoked if the attribute wasn't
            # found by __getattribute__
            #
            # optimization: sometimes we're asked for special attributes
            # such as __conform__ that we can disregard (because we
            # wouldn't be in here if the class had such an attribute
            # defined).
            # also handle special dynamic providedBy cache here.
            if name.startswith('__') or name == '_v__providedBy__':
                raise AttributeError(name)

            # attribute was not found; try to look it up in the schema and return
            # a default
            value = _default_from_schema(
                self,
                SCHEMA_CACHE.get(self.portal_type),
                name
            )
            if value is not _marker:
                return value

            # do the same for each subtype
            assignable = IBehaviorAssignable(self, None)
            if assignable is not None:
                for behavior_registration in assignable.enumerateBehaviors():
                    if behavior_registration.interface:
                        value = _default_from_schema(
                            self,
                            behavior_registration.interface,
                            name
                        )
                        if value is not _marker:
                            return value

            raise AttributeError(name)

        from plone.dexterity.content import DexterityContent
        from plone.dexterity.content import Item
        self.patch_refs(DexterityContent, '__getattr__', __getattr__)
        self.patch_refs(Item, '__getattr__', __getattr__)


class PatchDXCreateContentInContainer(MonkeyPatch):
    """Monkey patch Dexterity's createContentInContainer so that it sets
    default values for fields that haven't had a value passed in to the
    constructor.
    """

    def __call__(self):
        from opengever.base.default_values import set_default_values
        from plone.dexterity.interfaces import IDexterityFTI
        from plone.dexterity.utils import addContentToContainer
        from zope.component import createObject
        from zope.component import getUtility
        from zope.event import notify
        from zope.lifecycleevent import ObjectCreatedEvent

        def createContentWithDefaults(portal_type, container, **kw):
            fti = getUtility(IDexterityFTI, name=portal_type)
            content = createObject(fti.factory)
            set_default_values(content, container, kw)

            # Note: The factory may have done this already, but we want to be sure
            # that the created type has the right portal type. It is possible
            # to re-define a type through the web that uses the factory from an
            # existing type, but wants a unique portal_type!
            content.portal_type = fti.getId()

            for (key, value) in kw.items():
                setattr(content, key, value)

            notify(ObjectCreatedEvent(content))
            return content

        def createContentInContainer(container, portal_type, checkConstraints=True, **kw):
            # Also pass container to createContent so it is available for
            # determining default values
            content = createContentWithDefaults(portal_type, container, **kw)
            return addContentToContainer(
                container, content, checkConstraints=checkConstraints)

        from plone.dexterity import utils
        self.patch_refs(
            utils, 'createContentInContainer', createContentInContainer)


class PatchZ3CFormChangedField(MonkeyPatch):
    """Patch changedField() so that it doesn't simply rely on the DataManager
    to return a field's stored value (which triggers fallbacks to the field's
    default / missing_value), but uses our helper function to access the real
    stored value, taking the underlying storage into account.
    """

    def __call__(self):
        from opengever.base.default_values import get_persisted_value_for_field
        from persistent.interfaces import IPersistent
        from z3c.form import interfaces
        from z3c.formwidget.query.widget import QueryContext
        import zope.schema

        def changedField(field, value, context=None):
            """Figure if a field's value changed

            Comparing the value of the context attribute and the given value"""
            if context is None:
                context = field.context
            if context is None:
                # IObjectWidget madness
                return True
            if zope.schema.interfaces.IObject.providedBy(field):
                return True

            if not IPersistent.providedBy(context):
                # Field is not persisted, delegate to original implementation
                assert isinstance(context, QueryContext)
                return original_changedField(field, value, context)

            dm = zope.component.getMultiAdapter(
                (context, field), interfaces.IDataManager)

            if not dm.canAccess():
                # Can't get the original value, assume it changed
                return True

            # Determine the original value
            # Use a helper method that actually returns the persisted value,
            # *without* triggering any fallbacks to default values or
            # missing values.
            try:
                stored_value = get_persisted_value_for_field(context, field)
            except AttributeError:
                return True

            if stored_value != value:
                return True

            return False

        from z3c.form import util
        __patch_refs__ = False
        original_changedField = util.changedField
        self.patch_refs(util, 'changedField', changedField)
