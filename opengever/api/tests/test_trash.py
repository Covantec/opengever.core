from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrashable
from opengever.trash.trash import ITrashed


class TestTrashAPI(IntegrationTestCase):

    def setUp(self):
        super(TestTrashAPI, self).setUp()

    @browsing
    def test_trash_document(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.document.absolute_url() + '/@trash',
                     method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertTrue(ITrashed.providedBy(self.document))

    @browsing
    def test_trash_trashed_document_gives_bad_request(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.document.absolute_url() + '/@trash',
                     method='POST', headers={'Accept': 'application/json'})

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.document.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(
            browser.json[u'error'][u'message'], u'Already trashed')

    @browsing
    def test_trash_checked_out_document_gives_bad_request(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.document.absolute_url() + '/@checkout',
                     method='POST', headers={'Accept': 'application/json'})

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.document.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(
            browser.json[u'error'][u'message'],
            u'Can not trash a checked-out document')

    @browsing
    def test_trash_document_without_permission_gives_401(self, browser):
        self.login(self.administrator, browser)

        self.document.aq_parent.manage_permission(
            'opengever.trash: Trash content', roles=[], acquire=0)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.document.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(
            browser.json[u'message'],
            u'You are not authorized to access this resource.')

    @browsing
    def test_untrash_document(self, browser):
        self.login(self.administrator, browser)
        trasher = ITrashable(self.document)
        trasher.trash()
        browser.open(self.document.absolute_url() + '/@untrash',
                     method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertFalse(ITrashed.providedBy(self.document))

    @browsing
    def test_untrash_document_without_permission_gives_401(self, browser):
        self.login(self.administrator, browser)

        self.document.aq_parent.manage_permission(
            'opengever.trash: Untrash content', roles=[], acquire=0)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.document.absolute_url() + '/@untrash',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(
            browser.json[u'message'],
            u'You are not authorized to access this resource.')
