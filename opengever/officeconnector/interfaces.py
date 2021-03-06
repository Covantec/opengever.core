from zope import schema
from zope.interface import Interface


class IOfficeConnectorSettings(Interface):

    attach_to_outlook_enabled = schema.Bool(
        title=u'OfficeConnector Outlook support',
        description=u'Enable attach to Outlook with the new style '
        u'OfficeConnector URLs',
        default=False)

    direct_checkout_and_edit_enabled = schema.Bool(
        title=u'OfficeConnector direct checkout suppport',
        description=u'Enable direct checkout and edit with the new style '
        u'OfficeConnector URLs',
        default=False)


class IOfficeConnectorSettingsView(Interface):

    def is_attach_enabled():
        pass

    def is_checkout_enabled():
        pass
