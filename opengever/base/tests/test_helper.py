from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import obj2brain
from opengever.base.browser.helper import get_css_class


class TestCssClassHelpers(IntegrationTestCase):

    def test_document_obj_with_relation_flag(self):
        self.login(self.dossier_responsible)
        setattr(self.document, '_v__is_relation', True)
        self.assertEquals(
            get_css_class(self.document),
            'icon-docx is-document-relation')

    def test_document_brain_with_icon(self):
        self.login(self.dossier_responsible)
        brain = obj2brain(self.document)
        self.assertEquals(brain.getIcon, 'docx.png')
        self.assertEquals(get_css_class(brain), 'icon-docx')

    def test_document_obj_with_icon(self):
        self.login(self.dossier_responsible)
        setattr(self.document, '_v__is_relation', False)
        self.assertEquals(self.document.getIcon(), 'docx.png')
        self.assertEquals(get_css_class(self.document), 'icon-docx')

    def test_sablontemplate_brain_with_icon(self):
        self.login(self.dossier_responsible)
        brain = obj2brain(self.sablon_template)
        self.assertEquals(brain.getIcon, 'docx.png')
        self.assertEquals(get_css_class(brain), 'icon-docx')

    def test_sablontemplate_obj_with_icon(self):
        self.login(self.dossier_responsible)
        setattr(self.sablon_template, '_v__is_relation', False)
        self.assertEquals(self.sablon_template.getIcon(), 'docx.png')
        self.assertEquals(get_css_class(self.sablon_template), 'icon-docx')

    def test_proposaltemplate_brain_with_icon(self):
        self.login(self.dossier_responsible)
        brain = obj2brain(self.proposal_template)
        self.assertEquals(brain.getIcon, 'docx.png')
        self.assertEquals(get_css_class(brain), 'icon-docx')

    def test_proposaltemplate_obj_with_icon(self):
        self.login(self.dossier_responsible)
        setattr(self.proposal_template, '_v__is_relation', False)
        self.assertEquals(self.proposal_template.getIcon(), 'docx.png')
        self.assertEquals(get_css_class(self.proposal_template), 'icon-docx')
