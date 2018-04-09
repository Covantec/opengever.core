from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
import opengever
import os


class TestSablonTemplateValidation(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    @browsing
    def test_invalid_template_is_not_rejected(self, browser):
        self.login(self.administrator, browser)
        browser.open(
            self.templates,
            view='++add++opengever.meeting.sablontemplate',
        )
        invalid_template_path = os.path.join(
            os.path.dirname(opengever.testing.assets.__file__),
            'invalid_sablon_template.docx'
        )
        assert os.path.exists(invalid_template_path)
        with open(invalid_template_path) as sablon_template:
            browser.fill({
                'Title': u'Sablonv\xferlage',
                'File': sablon_template,
            }).save()
        statusmessages.assert_no_error_messages()

    @browsing
    def test_valid_template_is_accepted(self, browser):
        self.login(self.administrator, browser)
        browser.open(
            self.templates,
            view='++add++opengever.meeting.sablontemplate',
        )
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
