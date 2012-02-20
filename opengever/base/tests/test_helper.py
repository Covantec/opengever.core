from ftw.testing import MockTestCase
from opengever.base.browser.helper import get_css_class
from opengever.ogds.base import utils
from plone.i18n.normalizer import idnormalizer, IIDNormalizer


class TestCssClassHelpers(MockTestCase):

    def setUp(self):
        self.ori_get_client_id = utils.get_client_id
        get_client_id = self.mocker.replace(
            'opengever.ogds.base.utils.get_client_id', count=False)
        self.expect(get_client_id()).result('client1')

        self.mock_utility(idnormalizer, IIDNormalizer)

    def tearDown(self):
        utils.get_client_id = self.ori_get_client_id

    def test_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('ftw.obj.obj')

        self.replay()

        self.assertEquals(get_css_class(obj), 'contenttype-ftw-obj-obj')

    def test_forwarding(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.inbox.forwarding')

        self.replay()

        self.assertEquals(get_css_class(obj),
                          'contenttype-opengever-inbox-forwarding')

    def test_document_brain_with_icon(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.document.document')
        self.expect(brain.getIcon).result('icon_dokument_pdf.gif')

        self.replay()

        self.assertEquals(get_css_class(brain), 'icon-dokument_pdf')

    def test_document_obj_with_icon(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.document.document')
        self.expect(obj.getIcon()).result('icon_dokument_word.gif')

        self.replay()

        self.assertEquals(get_css_class(obj), 'icon-dokument_word')

    def test_document_obj_with_relation_flag(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.document.document')
        self.expect(hasattr(obj, '_v__is_relation')).result(True)

        self.replay()

        self.assertEquals(get_css_class(obj), 'icon-dokument_verweis')

    def test_task_brain(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.task.task')
        self.expect(brain.is_subtask).result(False)
        self.expect(brain.client_id).result('client1')
        self.expect(brain.assigned_client).result('client1')

        self.replay()

        self.assertEquals(get_css_class(brain),
                          'contenttype-opengever-task-task')

    def test_task_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.task.task')
        self.expect(obj.responsible_client).result('client1')

        parent = self.stub()
        self.set_parent(obj, parent)
        # parent is dossier -> obj is not subtask
        self.expect(parent.portal_type).result('opengever-dossier')

        self.replay()

        self.assertEquals(get_css_class(obj),
                          'contenttype-opengever-task-task')

    def test_subtask_brain(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.task.task')
        self.expect(brain.is_subtask).result(True)
        self.expect(brain.client_id).result('client1')
        self.expect(brain.assigned_client).result('client1')

        self.replay()

        self.assertEquals(get_css_class(brain),
                          'icon-task-subtask')

    def test_subtask_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.task.task')
        self.expect(obj.responsible_client).result('client1')

        parent = self.stub()
        self.set_parent(obj, parent)
        # parent is task -> obj is subtask
        self.expect(parent.portal_type).result('opengever.task.task')

        self.replay()

        self.assertEquals(get_css_class(obj),
                          'icon-task-subtask')

    def test_remote_task_brain(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.task.task')
        self.expect(brain.is_subtask).result(False)
        self.expect(brain.client_id).result('client1')
        self.expect(brain.assigned_client).result('client2')

        self.replay()

        self.assertEquals(get_css_class(brain),
                          'icon-task-remote-task')

    def test_remote_task_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.task.task')
        self.expect(obj.responsible_client).result('client2')

        parent = self.stub()
        self.set_parent(obj, parent)
        # parent is dossier -> obj is not subtask
        self.expect(parent.portal_type).result('opengever-dossier')

        self.replay()

        self.assertEquals(get_css_class(obj),
                          'icon-task-remote-task')
