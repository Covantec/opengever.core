from zope.interface import Interface


class IAppraisal(Interface):
    """The appraisal adapter Interface."""


class IHistoryStorage(Interface):
    """The history storage adapter Interface."""


class IDisposition(Interface):
    """The disposition Interface."""


class IDuringDossierDestruction(Interface):
    """Request layer to indicate that dossiers are currently being destroyed.
    """
