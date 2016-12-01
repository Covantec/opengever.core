from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition.interfaces import IAppraisal
from opengever.disposition.interfaces import IDisposition
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds


@implementer(IAppraisal)
@adapter(IDisposition)
class Appraisal(object):
    """Adapter for disposition objects, which stores the archival appraisal
    for each dossiers in the annotations of the context (disposition).
    """

    key = 'disposition_appraisal'

    def __init__(self, context):
        self.context = context
        self._annotations = IAnnotations(self.context)
        if self.key not in self._annotations.keys():
            self._annotations[self.key] = PersistentDict()

    @property
    def storage(self):
        return self._annotations[self.key]

    def initialize(self, dossier):
        intid = getUtility(IIntIds).getId(dossier)
        self.storage[intid] = self.is_archival_worthy(dossier)

    def is_archival_worthy(self, dossier):
        """Checks the preselection in the archive_value field and return
        if the dossier should be archived or not.
        """
        return ILifeCycle(dossier).archival_value != ARCHIVAL_VALUE_UNWORTHY

    def get(self, dossier):
        intid = getUtility(IIntIds).getId(dossier)
        return self.storage.get(intid)

    def update(self, dossier=None, intid=None, archive=True):
        if not intid and not dossier:
            raise ValueError('dossier or intid needed.')

        if not intid:
            intid = getUtility(IIntIds).getId(dossier)

        self.storage[intid] = archive

    def drop(self, dossier):
        intid = getUtility(IIntIds).getId(dossier)
        self.storage.pop(intid)

    def write_to_dossier(self, dossier):
        if self.get(dossier):
            ILifeCycle(dossier).archival_value = ARCHIVAL_VALUE_WORTHY

        else:
            ILifeCycle(dossier).archival_value = ARCHIVAL_VALUE_UNWORTHY