from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import _checkPermission
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
from zope.interface import noLongerProvides
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import queryMultiAdapter


class ITrashable(Interface):
    """Interface proveded by trashable content.
    """


class ITrashableMarker(Interface):
    """Marker interface for the trashable behavior.
    """


class ITrashed(Interface):
    """All Objects wich provide that interfaces
    are "moved to trash" (special delete functionality)
    """


class ITrashedEvent(IObjectEvent):
    """Interface of an event which gets fired when moving a document to trash.
    """


class IUntrashedEvent(IObjectEvent):
    """Interface of an event which gets fired when ractivating a trashed document.
    """


class TrashedEvent(ObjectEvent):
    """The event which gets fired when moving a document to trash.
    """

    implements(ITrashedEvent)


class UntrashedEvent(ObjectEvent):
    """The event which gets fired when reactivating a trashed document.
    """

    implements(IUntrashedEvent)


class TrashError(Exception):
    """An error that occurs during a trash/untrash operation."""


class Trasher(object):
    """An object which handles trashing/untrashing documents.
    """

    def __init__(self, context):
        self.context = context

    def trash(self):
        if not _checkPermission('opengever.trash: Trash content',
                                self.context):
            raise Unauthorized()

        folder = aq_parent(aq_inner(self.context))
        if not _checkPermission('opengever.trash: Trash content', folder):
            raise Unauthorized()

        if ITrashed.providedBy(self.context):
            raise TrashError('Already trashed')

        manager = queryMultiAdapter((self.context, self.context.REQUEST),
                                    ICheckinCheckoutManager)
        if manager and manager.get_checked_out_by():
            raise TrashError('Document checked out')

        alsoProvides(self.context, ITrashed)

        # Trashed objects will be filtered from catalog search results by
        # default via a monkey patch somewhere in opengever.base.monkey
        self.reindex()
        notify(TrashedEvent(self.context))

    def untrash(self):
        if not _checkPermission('opengever.trash: Untrash content', self.context):
            raise Unauthorized()

        folder = aq_parent(aq_inner(self.context))
        if not _checkPermission('opengever.trash: Trash content', folder):
            raise Unauthorized()

        noLongerProvides(self.context, ITrashed)

        self.reindex()
        notify(UntrashedEvent(self.context))

    def reindex(self):
        self.context.reindexObject(idxs=['trashed', 'object_provides'])
