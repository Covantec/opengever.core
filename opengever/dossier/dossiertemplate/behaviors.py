from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base import _ as base_mf
from opengever.dossier import _
from opengever.dossier.behaviors import dossiernamefromtitle
from opengever.dossier.behaviors.dossier import IDossier
from plone.app.content.interfaces import INameFromTitle
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface


class IDossierTemplateSchema(form.Schema):
    """Schema interface for dossier template types.

    Use this type of dossier to create a reusable template structures.
    """

    form.fieldset(
        u'common',
        label=base_mf(u'fieldset_common', default=u'Common'),
        fields=[
            u'title_help',
            u'predefined_keywords',
            u'restrict_keywords',
        ],
    )

    title_help = schema.TextLine(
        title=_(u'label_title_help', default=u'Title help'),
        description=_(u'help_title_help',
                      default=u'Recommendation for the title. Will be '
                              u'displayed as a help text if you create '
                              u'a dossier from template'),
        required=False,
    )

    form.order_after(predefined_keywords='IDossierTemplate.keywords')
    predefined_keywords = schema.Bool(
        title=_(u'label_predefined_keywords', default=u'Predefined Keywords'),
        required=False,
        missing_value=True,
        default=True,
    )

    form.order_after(restrict_keywords='predefined_keywords')
    restrict_keywords = schema.Bool(
        title=_(u'label_restrict_keywords', default=u'Restrict Keywords'),
        required=False,
        missing_value=False,
        default=False,
    )


class IDossierTemplateMarker(Interface, ITabbedviewUploadable):
    """Marker Interface for dossiertemplates.
    """


class IDossierTemplate(IDossier):
    """Behavior Interface for dossiertemplates.

    We need the IDossier behavior fields for the dossier template.
    Unfortunately we cannot use the IDossier behavior directly because
    it's providing the IDossierMarker interface which will destroy
    some functionality of the dossiertemplate.

    To fix that, we have to create a subclass of the IDosser behavior
    and register it with an own IDossierTemplateMarker interface.

    With this workaround we get the schema of the IDossier but
    not its marker interfaces.
    """

alsoProvides(IDossierTemplate, IFormFieldProvider)


class IDossierTemplateNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class DossierTemplateNameFromTitle(dossiernamefromtitle.DossierNameFromTitle):
    """Choose IDs for a dossiertemplate in the following format:
    'dossiertemplate-{sequence number}'
    """

    implements(IDossierTemplateNameFromTitle)

    format = u'dossiertemplate-%i'


class IRestrictAddableDossierTemplates(form.Schema):

    addable_dossier_templates = RelationList(
        title=_(u'label_addable_dossier_templates',
                default=u'Addable dossier templates'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u'Addable dossiertemplate',
            source=ObjPathSourceBinder(
                portal_type=("opengever.dossier.dossiertemplate"),
                is_subdossier=False,
                navigation_tree_query={
                    'object_provides':
                    ['opengever.dossier.templatefolder.interfaces.ITemplateFolder',
                     'opengever.dossier.dossiertemplate.behaviors.IDossierTemplateSchema']
                }),
            ),
        required=False,
    )


alsoProvides(IRestrictAddableDossierTemplates, IFormFieldProvider)
