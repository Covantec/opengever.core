from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base import pdfconverter
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.testing import FunctionalTestCase


class TestDocumentLinkWidget(FunctionalTestCase):

    @browsing
    def test_link_contains_mimetype_icon_clas(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())

        link = browser.css('a.document_link').first
        self.assertEquals('tabbedview-tooltip document_link icon-doc',
                          link.get('class'))

    @browsing
    def test_tooltip_link_is_documents_tooltip_view(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())
        link = browser.css('a.document_link').first
        self.assertEquals('http://nohost/plone/document-1/tooltip',
                          link.get('data-tooltip-url'))

    @browsing
    def test_is_linked_to_the_object(self, browser):
        document = create(Builder('document')
                          .titled('Anfrage Meier')
                          .with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())

        link = browser.css('a.document_link').first
        self.assertEquals('Anfrage Meier', link.text)
        self.assertEquals(document.absolute_url(), link.get('href'))

    @browsing
    def test_removed_documents_are_prefixed_with_removed_marker(self, browser):
        document_a = create(Builder('document').with_dummy_content())
        document_b = create(Builder('document').with_dummy_content().removed())

        browser.open_html(DocumentLinkWidget(document_a).render())
        self.assertEquals([], browser.css('.removed_document'))

        browser.open_html(DocumentLinkWidget(document_b).render())
        self.assertEquals(1, len(browser.css('.removed_document')))


class TestDocumentLinkWidgetWithActivatedBumblebee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_document_link_is_extended_with_showrom_data(self, browser):
        document = create(Builder('document').with_dummy_content())

        browser.open_html(DocumentLinkWidget(document).render())

        link = browser.css('a.document_link').first
        self.assertIn('showroom-item', link.get('class'))
        self.assertEquals(
            'http://nohost/plone/document-1/@@bumblebee-overlay-listing',
            link.get('data-showroom-target'))
        self.assertEquals(
            u'Testdokum\xe4nt',
            link.get('data-showroom-title'))
