from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
import opengever
import os


class RedirectorTests(IntegrationTestCase):

    @browsing
    def test_sablon_template_redirector(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.templates, view='++add++opengever.meeting.sablontemplate')
        valid_template_path = os.path.join(
            os.path.dirname(opengever.testing.assets.__file__),
            'valid_sablon_template.docx'
        )
        assert os.path.exists(valid_template_path)
        with open(valid_template_path) as sablon_template:
            browser.fill({
                'Title': u'Sablonv\xferlage',
                'File': sablon_template,
            }).save()
        statusmessages.assert_no_error_messages()

        self.assertEquals('http://nohost/plone/vorlagen#sablontemplates-proxy',
                          browser.url)
