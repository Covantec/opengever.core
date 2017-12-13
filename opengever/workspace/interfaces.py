from zope import schema
from zope.interface import Interface


class IWorkspaceRoot(Interface):
    """ Marker interface for Workspace Roots """


class IWorkspace(Interface):
    """ Marker interface for Workspace """


class IWorkspaceSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable workspace feature',
        description=u'Whether workspace integration is enabled',
        default=False)
