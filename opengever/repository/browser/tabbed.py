from opengever.repository import _
from opengever.tabbedview import GeverTabbedView
from plone import api


class RepositoryRootTabbedView(GeverTabbedView):
    """Define the tabs available on a Repository Root."""

    overview_tab = {
        'id': 'overview',
        'title': _(u'label_overview', default=u'Overview'),
        }

    dossiers_tab = {
        'id': 'dossiers',
        'title': _(u'label_dossiers', default=u'Dossiers'),
        }

    info_tab = {
        'id': 'sharing',
        'title': _(u'label_info', default=u'Info'),
        }

    @property
    def dispositions_tab(self):
        if api.user.has_permission('opengever.disposition: Add disposition', obj=self.context):
            return {
                'id': 'dispositions',
                'title': _(u'label_dispositions', default=u'Dispositions'),
                }

        return None

    @property
    def journal_tab(self):
        if api.user.has_permission('Sharing page: Delegate roles', obj=self.context):
            return {
                'id': 'journal',
                'title': _(u'label_journal', default=u'Journal'),
                }

        return None

    def _get_tabs(self):
        return filter(None, [
            self.overview_tab,
            self.dossiers_tab,
            self.dispositions_tab,
            self.info_tab,
            self.journal_tab,
        ])


class RepositoryFolderTabbedView(GeverTabbedView):
    """Define the tabs available on a Repository Root."""

    dossiers_tab = {
        'id': 'dossiers',
        'title': _(u'label_dossiers', default=u'Dossiers'),
        }

    info_tab = {
        'id': 'sharing',
        'title': _(u'label_info', default=u'Info'),
        }

    def _get_tabs(self):
        return filter(None, [
            self.dossiers_tab,
            self.info_tab,
        ])
