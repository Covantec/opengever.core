from datetime import date
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.schema import TableChoice
from opengever.contact import is_contact_feature_enabled
from opengever.contact.sources import ContactsSourceBinder
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier import _
from opengever.document.oneoffixx.command import CreateDocumentFromOneOffixxTemplateCommand
from opengever.tabbedview.helper import document_with_icon
from plone import api
from plone.autoform import directives as form
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable
from z3c.form import button
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.form import Form
from z3c.form.field import Fields
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


def get_oneoffixx_templates():
    """
    We don't have the API for oneoffixx, so for now we mock it.
    """
    templates = [
        {'title': u'Briefvorlage A4',
         'template-id': 234,
         'created': date(2018, 2, 3),
         'group': 'Briefe'},
        {'title': u'Briefvorlage A5',
         'template-id': 32,
         'created': date(2018, 2, 3),
         'group': 'Briefe'},
        {'title': u'Vorlage OGIP',
         'template-id': 14,
         'created': date(2018, 2, 3),
         'group': 'Documente'},
        {'title': u'Kurzbrief',
         'template-id': 15,
         'created': date(2018, 2, 3),
         'group': 'Briefe'}
    ]
    return templates


@provider(IContextSourceBinder)
def get_templates(context):
    """Return a list available templates
    """
    templates = get_oneoffixx_templates()

    template_group = context.REQUEST.form.get('form.widgets.template_group')
    terms = []
    for template in templates:
        terms.append(SimpleVocabulary.createTerm(
                     oneofixx_template(template),
                     str(template.get("template-id")),
                     template.get("title")))
    if template_group is not None and template_group[0] != '--NOVALUE--':
        terms = [term for term in terms if term.value.group == template_group[0]]
    return MutableObjectVocabulary(terms)


@provider(IContextSourceBinder)
def get_template_groups(context):
    """Return the list of available template groups
    """
    templates = get_oneoffixx_templates()
    groups = set([template.get("group") for template in templates])
    terms = []
    for group in groups:
        terms.append(SimpleVocabulary.createTerm(group, group, group))
    return MutableObjectVocabulary(terms)


class oneofixx_template(object):

    def __init__(self, obj):
        self.title = obj.get("title")
        self.template_id = obj.get("template-id")
        self.group = obj.get("group")
        self.filename = unicode(obj.get("template-id"))

    def __eq__(self, other):
        if type(other) == type(self):
            return self.title == other.title
        return False


class MutableObjectVocabulary(SimpleVocabulary):

    def __contains__(self, value):
        try:
            return any([value == val for val in self.by_value])
        except TypeError:
            return False


class ICreateDocumentFromOneOffixxTemplate(model.Schema):

    template_group = schema.Choice(
        title=_(u'label_template_group', default=u'Template group'),
        source=get_template_groups,
        required=False,
    )

    template = TableChoice(
        title=_(u"label_template", default=u"Template"),
        source=get_templates,
        required=True,
        show_filter=False,
        vocabulary_depends_on=['form.widgets.template_group'],
        columns=(
            {'column': 'title',
             'column_title': _(u'label_title', default=u'Title'),
             'sort_index': 'sortable_title'},
            )
    )

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True)

    form.widget(edit_after_creation=SingleCheckBoxFieldWidget)
    edit_after_creation = schema.Bool(
        title=_(u'label_edit_after_creation', default='Edit after creation'),
        default=True,
        required=False,
        )


class SelectOneOffixxTemplateDocumentWizardStep(Form):

    label = _(u'create_document_with_template',
              default=u'Create document from template')
    ignoreContext = True
    fields = Fields(ICreateDocumentFromOneOffixxTemplate)

    def finish_document_creation(self, data):
        new_doc = self.create_document(data)

        if data.get('edit_after_creation'):
            self.activate_external_editing(new_doc)
            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '#documents')

    def activate_external_editing(self, new_doc):
        """Check out the given document, and add the external_editor URL
        to redirector queue.
        """
        # Check out the new document
        manager = self.context.restrictedTraverse('checkout_documents')
        manager.checkout(new_doc)

        new_doc.setup_external_edit_redirect(self.request)

    def create_document(self, data):
        """Create a new document based on a template."""

        command = CreateDocumentFromOneOffixxTemplateCommand(
            self.context, data['title'], data['template'])
        return command.execute()

    @button.buttonAndHandler(_('button_save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        return self.finish_document_creation(data)

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class SelectOneOffixxTemplateDocumentView(FormWrapper):

    form = SelectOneOffixxTemplateDocumentWizardStep

