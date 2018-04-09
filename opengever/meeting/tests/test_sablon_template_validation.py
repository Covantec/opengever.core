from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import assets
from opengever.testing import IntegrationTestCase


class TestSablonTemplateValidation(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    @browsing
    def test_invalid_template_is_not_rejected(self, browser):
        self.login(self.administrator, browser)
        browser.open(
            self.templates,
            view='++add++opengever.meeting.sablontemplate',
        )
        sablon_template = assets.load('invalid_sablon_template.docx')
        browser.fill({
            'Title': u'Sablonv\xferlage',
            'File': (sablon_template, 'valid_sablon_template.docx', 'text/plain'),
        }).save()
        statusmessages.assert_no_error_messages()

    @browsing
    def test_valid_template_is_accepted(self, browser):
        self.login(self.administrator, browser)
        browser.open(
            self.templates,
            view='++add++opengever.meeting.sablontemplate',
        )
        sablon_template = assets.load('valid_sablon_template.docx')
        browser.fill({
            'Title': u'Sablonv\xferlage',
            'File': sablon_template,
        }).save()
        statusmessages.assert_no_error_messages()
