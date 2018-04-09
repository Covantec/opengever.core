from opengever.base.command import BaseObjectCreatorCommand
from zope.annotation.interfaces import IAnnotations
#from plone.namedfile.file import NamedBlobFile


class CreateDocumentFromOneOffixxTemplateCommand(BaseObjectCreatorCommand):
    """Store a copy of the template in the new document's primary file field
    """

    portal_type = 'opengever.document.document'
    primary_field_name = 'file'

    def __init__(self, context, title, template):
        self.template_id = template.template_id
        self.filename = template.filename
        super(CreateDocumentFromOneOffixxTemplateCommand, self).__init__(
            context, title)
        #self.additional_args.update({
        #    self.primary_field_name: NamedBlobFile(
        #        filename=self.filename)})

    def execute(self):
        obj = super(CreateDocumentFromOneOffixxTemplateCommand, self).execute()
        annotations = IAnnotations(obj)
        annotations["template-id"] = self.template_id
        return obj.as_shadow_document()
