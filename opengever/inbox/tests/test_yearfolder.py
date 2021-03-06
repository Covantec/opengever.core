from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ooxml_docprops import read_properties
from opengever.dossier.docprops import TemporaryDocFile
from opengever.task.browser.accept.utils import get_current_yearfolder
from opengever.task.interfaces import IYearfolderStorer
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestYearFolderGetter(FunctionalTestCase):

    def setUp(self):
        super(TestYearFolderGetter, self).setUp()

        self.inbox_container = create(Builder('inbox_container'))
        self.client1_inbox = create(Builder('inbox')
                                    .within(self.inbox_container)
                                    .having(responsible_org_unit='client1'))
        self.client2_inbox = create(Builder('inbox')
                                    .within(self.inbox_container)
                                    .having(responsible_org_unit='client2'))

        self.current_year = unicode(date.today().year)

    def test_returns_yearfolder_of_the_current_year(self):
        yearfolder = create(Builder('yearfolder')
                            .within(self.client1_inbox)
                            .having(id=self.current_year))

        self.assertEquals(self.current_year, yearfolder.getId())
        self.assertEquals(yearfolder,
                          get_current_yearfolder(inbox=self.client1_inbox))

    def test_creates_yearfolder_of_the_current_year_when_not_exists(self):
        yearfolder = get_current_yearfolder(inbox=self.client1_inbox)

        self.assertEquals(self.current_year, yearfolder.getId())
        self.assertEquals('Closed {}'.format(self.current_year),
                          yearfolder.Title())

    def test_observe_current_inbox_when_context_is_given(self):
        client1_yearfolder = create(Builder('yearfolder')
                                    .within(self.client1_inbox)
                                    .having(id=self.current_year))

        create(Builder('yearfolder')
               .within(self.client2_inbox)
               .having(id=self.current_year))

        self.assertEquals(client1_yearfolder,
                          get_current_yearfolder(context=self.portal))

    def test_raises_when_both_context_and_inbox_are_missing(self):
        with self.assertRaises(ValueError) as cm:
            get_current_yearfolder()

        self.assertEquals(
            'Context or the current inbox itself must be given.',
            str(cm.exception))


class TestYearFolderStorer(FunctionalTestCase):

    def setUp(self):
        super(TestYearFolderStorer, self).setUp()
        self.set_docproperty_export_enabled(True)

    def tearDown(self):
        self.set_docproperty_export_enabled(False)
        super(TestYearFolderStorer, self).tearDown()

    def test_disable_docproperty_updating(self):
        inbox = create(Builder('inbox'))
        forwarding = create(Builder('forwarding').within(inbox))
        doc = create(Builder('document')
                     .within(forwarding)
                     .titled("Document with file")
                     .with_asset_file('with_gever_user_properties.docx'))

        IYearfolderStorer(forwarding).store_in_yearfolder()

        with TemporaryDocFile(doc.file) as tmpfile:
            properties = dict(read_properties(tmpfile.path))
            self.assertItemsEqual(TEST_USER_ID, properties.get('User.ID'))
