from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import dexterity
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from opengever.base.oguid import Oguid
from opengever.meeting.model import Committee
from opengever.testing import IntegrationTestCase


class TestCommittee(IntegrationTestCase):

    features = ('meeting',)

    group_field_name = 'Group'

    def test_committee_id_is_generated(self):
        self.login(self.administrator)
        self.assertEqual('committee-1', self.committee.getId())

    def test_committee_model_is_initialized_correctly(self):
        self.login(self.administrator)
        model = self.committee.load_model()

        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(self.committee), model.oguid)

    def test_get_toc_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.committee.toc_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_toc_template())

    def test_get_toc_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.committee_container.toc_template = self.as_relation_value(
            self.sablon_template)

        self.assertIsNone(self.committee.toc_template)
        self.assertEqual(
            self.sablon_template, self.committee.get_toc_template())

    def test_get_excerpt_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.committee.excerpt_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_excerpt_template())

    def test_get_excerpt_template_falls_back_to_container(self):
        self.login(self.administrator)

        self.assertIsNone(self.committee.excerpt_template)
        self.assertIsNotNone(self.committee_container.excerpt_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_excerpt_template())

    @browsing
    def test_committee_repository_is_validated(self, browser):
        self.login(self.administrator, browser)

        browser.open(self.committee_container,
                     view='++add++opengever.meeting.committee')

        browser.fill(
            {'Title': u'A c\xf6mmittee',
             'Linked repository folder': self.branch_repofolder,
             self.group_field_name: 'committee_rpk_group'})
        browser.css('#form-buttons-save').first.click()

        self.assertEqual('You cannot add dossiers in the selected repository '
                         'folder. Either you do not have the privileges or '
                         'the repository folder contains another repository '
                         'folder.',
                         dexterity.erroneous_fields()['fuhrung'][0])

    @browsing
    def test_committee_can_be_created_in_browser(self, browser):
        self.login(self.administrator, browser)

        browser.open(self.committee_container,
                     view='++add++opengever.meeting.committee')

        browser.fill(
            {'Title': u'A c\xf6mmittee',
             'Protocol template': self.sablon_template,
             'Excerpt template': self.sablon_template,
             'Table of contents template': self.sablon_template,
             'Linked repository folder': self.leaf_repofolder,
             self.group_field_name: 'committee_rpk_group'})
        browser.css('#form-buttons-save').first.click()

        browser.fill({'Title': u'Initial',
                      'Start date': '01.01.2012',
                      'End date': '31.12.2012'}).submit()

        statusmessages.assert_message('Item created')

        committee = browser.context
        self.assertEqual('committee-3', committee.getId())
        self.assertEqual(
            ('CommitteeResponsible', 'Editor'),
            dict(committee.get_local_roles()).get('committee_rpk_group'))
        self.assertEqual(self.leaf_repofolder,
                         committee.get_repository_folder())
        self.assertEqual(self.sablon_template,
                         committee.get_protocol_template())
        self.assertEqual(self.sablon_template,
                         committee.get_excerpt_template())
        self.assertEqual(self.sablon_template,
                         committee.get_toc_template())

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(committee), model.oguid)
        self.assertEqual(u'A c\xf6mmittee', model.title)

        self.assertEqual(1, len(model.periods))
        period = model.periods[0]
        self.assertEqual('active', period.workflow_state)
        self.assertEqual(u'Initial', period.title)
        self.assertEqual(date(2012, 1, 1), period.date_from)
        self.assertEqual(date(2012, 12, 31), period.date_to)

    @browsing
    def test_committee_can_be_edited_in_browser(self, browser):
        self.login(self.committee_responsible, browser)

        local_roles = dict(self.committee.get_local_roles())
        self.assertIn('committee_rpk_group', local_roles)
        self.assertNotIn('committee_ver_group', local_roles)

        browser.open(self.committee, view='edit')
        form = browser.forms['form']

        self.assertEqual(u'Rechnungspr\xfcfungskommission',
                         form.find_field('Title').value)

        browser.fill({'Title': u'A c\xf6mmittee',
                      self.group_field_name: u'committee_ver_group'})
        browser.css('#form-buttons-save').first.click()

        statusmessages.assert_message('Changes saved')

        committee = browser.context
        local_roles = dict(committee.get_local_roles())
        self.assertEqual('committee-1', committee.getId())
        self.assertNotIn('committee_rpk_group', local_roles,)
        self.assertEqual(('CommitteeResponsible', 'Editor'),
                         local_roles.get('committee_ver_group'))

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(u'A c\xf6mmittee', model.title)


class TestCommitteeWorkflow(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_active_committee_can_be_deactivated(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.empty_committee)

        editbar.menu_option('Actions', 'deactivate').click()

        self.assertEqual(Committee.STATE_INACTIVE,
                         self.empty_committee.load_model().get_state())
        statusmessages.assert_message('Committee deactivated successfully')

    def test_initial_state_is_active(self):
        self.login(self.committee_responsible)
        self.assertEqual(Committee.STATE_ACTIVE,
                         self.empty_committee.load_model().get_state())

    @browsing
    def test_deactivating_is_not_possible_when_pending_meetings_exists(
            self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee)

        editbar.menu_option('Actions', 'deactivate').click()

        self.assertEqual(Committee.STATE_ACTIVE,
                         self.committee.load_model().get_state())
        statusmessages.assert_message('Not all meetings are closed.')

    @browsing
    def test_deactivating_not_possible_when_unscheduled_proposals_exist(
            self, browser):
        self.login(self.committee_responsible, browser)
        create(
            Builder('proposal').within(self.dossier)
            .having(title=u'Non-scheduled proposal',
                    committee=self.empty_committee.load_model())
            .as_submitted())
        browser.open(self.empty_committee)

        editbar.menu_option('Actions', 'deactivate').click()

        self.assertEqual(Committee.STATE_ACTIVE,
                         self.committee.load_model().get_state())
        statusmessages.assert_message(
            'There are unscheduled proposals submitted to this committee.')

    @browsing
    def test_deactivated_comittee_can_be_reactivated(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.empty_committee)

        editbar.menu_option('Actions', 'deactivate').click()
        editbar.menu_option('Actions', 'reactivate').click()

        self.assertEqual(Committee.STATE_ACTIVE,
                         self.empty_committee.load_model().get_state())
        statusmessages.assert_message('Committee reactivated successfully')

    @browsing
    def test_adding_is_not_available_in_inactive_committee(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.empty_committee)

        self.assertEqual([u'Add new', u'Actions'], editbar.menus())

        editbar.menu_option('Actions', 'deactivate').click()
        self.assertEqual([u'Actions'], editbar.menus())
