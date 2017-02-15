from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from ftw.builder import Builder
from ftw.builder import create
from opengever.bundle.loader import BundleLoader
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.bundle.sections.fileloader import FileLoaderSection
from opengever.bundle.tests import MockTransmogrifier
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestFileLoader(FunctionalTestCase):

    def setup_section(self, previous=None):
        previous = previous or []
        self.transmogrifier = MockTransmogrifier()
        self.transmogrifier.context = api.portal.get()

        self.bundle_path = resource_filename(
            'opengever.bundle.tests', 'assets/basic.oggbundle')
        self.bundle = BundleLoader(self.bundle_path).load()
        IAnnotations(self.transmogrifier)[BUNDLE_PATH_KEY] = self.bundle_path
        IAnnotations(self.transmogrifier)[BUNDLE_KEY] = self.bundle
        options = {'blueprint': 'opengever.setup.fileloader'}

        return FileLoaderSection(self.transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(FileLoaderSection))
        verifyClass(ISection, FileLoaderSection)

        self.assertTrue(ISectionBlueprint.providedBy(FileLoaderSection))
        verifyObject(ISectionBlueprint, FileLoaderSection)

    def test_loads_file_into_existing_document(self):
        doc = create(Builder('document').titled('Foo Bar'))
        self.assertIsNone(doc.file)
        relative_path = '/'.join(doc.getPhysicalPath()[2:])
        item = {
            u"_type": u"opengever.document.document",
            u"_path": relative_path,
            u"filepath": u"files/beschluss.pdf",
            u"_object": doc,
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual('Lorem Ipsum\n', doc.file.data)
        self.assertEqual('application/pdf', doc.file.contentType)
        self.assertEqual('foo-bar.pdf', doc.file.filename)

    def test_syncs_title_from_filename_if_untitled(self):
        doc = create(Builder('document').titled(None))
        self.assertIsNone(doc.file)
        relative_path = '/'.join(doc.getPhysicalPath()[2:])
        item = {
            u"_type": u"opengever.document.document",
            u"_path": relative_path,
            u"filepath": u"files/beschluss.pdf",
            u"_object": doc,
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual('beschluss.pdf', doc.file.filename)
        self.assertEqual('beschluss', doc.title)

    def test_tracks_missing_files_in_errors(self):
        item = {
            u"_type": u"opengever.document.document",
            u"_path": '/relative/path/to/doc',
            u"filepath": u"files/missing.file",
        }
        section = self.setup_section(previous=[item])
        list(section)

        abs_filepath = '/'.join((self.bundle_path, 'files/missing.file'))
        self.assertEqual(
            {abs_filepath: '/relative/path/to/doc'},
            self.bundle.errors['files_not_found'])

    def test_tracks_unmapped_unc_files_in_errors(self):
        item = {
            u"_type": u"opengever.document.document",
            u"_path": '/relative/path/to/doc',
            u"filepath": u'\\\\host\\unmapped\\foo.docx',
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual(
            set([u'\\\\host\\unmapped']),
            self.bundle.errors['unmapped_unc_mounts'])

        self.assertEqual(
            [item['filepath']],
            self.bundle.errors['unresolvable_filepaths'])

    def test_tracks_skipped_msg_files_in_errors(self):
        item = {
            u"_type": u"opengever.document.document",
            u"_path": '/relative/path/to/doc',
            u"filepath": u"files/outlook.msg",
        }
        section = self.setup_section(previous=[item])
        list(section)

        abs_filepath = '/'.join((self.bundle_path, 'files/outlook.msg'))
        self.assertEqual(
            {abs_filepath: '/relative/path/to/doc'},
            self.bundle.errors['msgs'])

    def test_handles_eml_mails(self):
        mail = create(Builder('mail'))
        self.assertIsNone(mail.message)
        relative_path = '/'.join(mail.getPhysicalPath()[2:])
        item = {
            u"_type": u"ftw.mail.mail",
            u"_path": relative_path,
            u"filepath": u"files/sample.eml",
            u"_object": mail,
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual(u'Lorem Ipsum', mail.title)
        self.assertEqual(920, len(mail.message.data))
        self.assertEqual('message/rfc822', mail.message.contentType)
        self.assertEqual('lorem-ipsum.eml', mail.message.filename)
        self.assertEqual(True, mail.digitally_available)
