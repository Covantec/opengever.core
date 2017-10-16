from opengever.dossier import _
from opengever.tabbedview.browser.tabs import Dossiers
from opengever.tabbedview.browser.tabs import SubDossiers


FILING_NO_COLUMN = {
    'column': 'filing_no',
    'column_title': _(u'filing_number', default=u'Filing Number')}


class DossiersFilingNumberIncluded(Dossiers):

    @property
    def columns(self):
        """Append the filing number column.
        """
        columns = super(DossiersFilingNumberIncluded, self).columns

        return columns + (FILING_NO_COLUMN, )


class SubDossiersFilingNumberIncluded(SubDossiers):

    @property
    def columns(self):
        """Append the filing number column.
        """
        columns = super(SubDossiersFilingNumberIncluded, self).columns

        return columns + (FILING_NO_COLUMN, )
