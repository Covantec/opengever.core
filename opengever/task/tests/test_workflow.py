from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
import transaction


class TestTaskWorkflow(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestTaskWorkflow, self).setUp()
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')

    def test_document_in_a_closed_tasks_are_still_editable(self):
        self.grant('Editor')
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID)
                      .in_state('task-state-tested-and-closed'))

        document = create(Builder('document')
                          .within(task))

        self.browser.open('%s/edit' % (document.absolute_url()))
        self.browser.fill({'Title': 'New Title'})
        self.browser.click('Save')

        self.browser.assert_portal_message('Changes saved')

    def test_editing_document_inside_a_task_inside_a_closed_dossier_raise_unauthorized(self):
        self.grant('Editor', 'Reviewer')
        dossier = create(Builder('dossier'))

        task = create(Builder('task')
                      .within(dossier)
                      .having(issuer=TEST_USER_ID, responsible=TEST_USER_ID)
                      .in_state('task-state-tested-and-closed'))

        document = create(Builder('document').within(task))

        self.wf_tool.doActionFor(dossier, 'dossier-transition-resolve')
        transaction.commit()

        with self.assertRaises(Unauthorized) as cm:
            self.browser.open('%s/edit' % (document.absolute_url()))

        self.assertEquals(
            'You are not authorized to access this resource.',
            str(cm.exception))

    def test_deleting_task_is_only_allowed_for_managers(self):
        task = create(Builder('task'))

        acl_users = api.portal.get_tool('acl_users')
        valid_roles = list(acl_users.portal_role_manager.valid_roles())
        valid_roles.remove('Manager')
        self.grant(*valid_roles)

        with self.assertRaises(Unauthorized):
            api.content.delete(obj=task)
