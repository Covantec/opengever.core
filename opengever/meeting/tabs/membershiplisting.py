from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting.model import Membership
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.base import BaseTableSource
from zope.interface import implements
from zope.interface import Interface


class IMembershipTableSourceConfig(ITableSourceConfig):
    """Marker interface for membership table source configs."""


class MembershipListingTab(BaseListingTab):
    implements(IMembershipTableSourceConfig)

    model = Membership

    columns = (
        {'column': '',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': lambda item, value: item.member.fullname},

        {'column': '',
         'column_title': _(u'column_date_from', default=u'Date from'),
         'transform': lambda item, value: item.get_date_from()},

        {'column': '',
         'column_title': _(u'column_date_to', default=u'Date to'),
         'transform': lambda item, value: item.get_date_to()},

        {'column': 'role',
         'column_title': _(u'column_role', default=u'Role'),
         'transform': lambda item, value: item.role},
        )

    def get_base_query(self):
        return Membership.query.filter_by(committee=self.context.load_model())


class MembershipTableSource(BaseTableSource):
    grok.implements(ITableSource)
    grok.adapts(MembershipListingTab, Interface)

    searchable_columns = []
