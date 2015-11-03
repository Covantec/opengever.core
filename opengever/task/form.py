from five import grok
from opengever.ogds.base.utils import ogds_service
from opengever.task import _
from opengever.task.activities import TaskAddedActivity
from opengever.task.task import ITask
from plone.directives import dexterity
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import getMultiAdapter


REASSIGN_TRANSITION = 'task-transition-reassign'


# XXX
# setting the default value of a RelationField does not work as expected
# or we don't know how to set it.
# thus we use an add form hack by injecting the values into the request.

class AddForm(dexterity.AddForm):
    grok.name('opengever.task.task')

    def update(self):
        # put default value for relatedItems into request
        paths = self.request.get('paths', [])
        if paths:
            self.request.set('form.widgets.relatedItems', paths)
        # put default value for issuer into request
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        member = portal_state.member()
        if not self.request.get('form.widgets.issuer', None):
            self.request.set('form.widgets.issuer', [member.getId()])
        super(AddForm, self).update()

        # omit the responsible_client field and adjust the field description
        # of the responsible field if there is only one orgunit configured.
        if not ogds_service().has_multiple_org_units():
            self.groups[0].widgets['responsible_client'].mode = HIDDEN_MODE
            self.groups[0].widgets['responsible'].field.description = _(
                u"help_responsible_single_client_setup", default=u"")

    def createAndAdd(self, data):
        task = super(AddForm, self).createAndAdd(data=data)
        activity = TaskAddedActivity(task, self.request, self.context)
        activity.record()
        return task


class EditForm(dexterity.EditForm):
    """Standard EditForm, just require the Edit Task permission"""
    grok.context(ITask)
    grok.require('opengever.task.EditTask')

    def update(self):
        super(EditForm, self).update()

        # omit the responsible_client field and adjust the field description
        # of the responsible field if there is only one client configured.
        if not ogds_service().has_multiple_org_units():
            self.groups[0].widgets['responsible_client'].mode = HIDDEN_MODE
            self.groups[0].widgets['responsible'].field.description = _(
                u"help_responsible_single_client_setup", default=u"")
