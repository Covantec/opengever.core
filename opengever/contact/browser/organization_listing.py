from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.contact import _
from opengever.contact.browser.person_listing import ActiveOnlyFilter
from opengever.contact.interfaces import IContactFolder
from opengever.contact.models import Organization
from opengever.tabbedview import _ as tmf
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.helper import boolean_helper
from opengever.tabbedview.helper import linked_sql_object
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.interface import Interface


class IOrganizationTableSourceConfig(ITableSourceConfig):
    """Marker interface for organization table source configs."""


class OrganizationListingTab(BaseListingTab):
    implements(IOrganizationTableSourceConfig)

    model = Organization

    @property
    def columns(self):
        return (
            {'column': 'name',
             'column_title': _(u'column_name', default=u'Name'),
             'transform': linked_sql_object},

            {'column': 'is_active',
             'column_title': _(u'column_active', default=u'Active'),
             'transform': boolean_helper}
        )

    def get_base_query(self):
        return Organization.query


class OrganizationTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(OrganizationListingTab, Interface)

    searchable_columns = [Organization.name]


class Organizations(OrganizationListingTab):
    grok.name('tabbedview_view-organizations')
    grok.context(IContactFolder)

    selection = ViewPageTemplateFile("templates/no_selection.pt")
    sort_on = 'name'

    show_selects = False
    filterlist_name = 'organization_state_filter'
    filterlist_available = True
    filterlist = FilterList(
        Filter('filter_all', tmf('all')),
        ActiveOnlyFilter('filter_active', tmf('Active'), default=True))

    enabled_actions = []
    major_actions = []
