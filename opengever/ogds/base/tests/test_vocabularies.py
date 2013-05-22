from opengever.ogds.base import communication
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.testing import create_contacts
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.vocabulary import ContactsVocabulary
from opengever.testing import FunctionalTestCase
from zope.component import getUtility
from zope.component import provideUtility
from zope.globalrequest import setRequest
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
import types


def fterms(data):
    """Formats terms for printing"""
    if isinstance(data, types.ListType):
        return [fterms(item) for item in data]
    elif isinstance(data, types.TupleType):
        return tuple([fterms(item) for item in data])
    elif isinstance(data, SimpleTerm):
        return '<Term %s:%s>' % (data.value, data.title)
    elif isinstance(data, types.GeneratorType):
        return fterms(list(data))
    else:
        return data


class TestVocabularies(FunctionalTestCase):

    def test_vocabularies(self):

        request = self.layer.get('request')

        from opengever.testing import set_current_client_id
        set_current_client_id(self.portal)

        # Test searchable vocabulary
        # ==========================
        # See `opengever.ogds.base.vocabulary`
        # Test our custom searchable vocabulary:
        def key_value_provider():
            yield ('first-entry', 'First Entry')
            yield ('second-entry', 'Second Entry')
            yield ('third-entry', 'Third Entry')
            yield ('fourth-entry', 'Fourth')

        self.assertEquals(
            [u'<Term first-entry:First Entry>',
             u'<Term second-entry:Second Entry>',
             u'<Term third-entry:Third Entry>',
             u'<Term fourth-entry:Fourth>'],
            fterms(ContactsVocabulary.get_terms_from_provider(key_value_provider)))

        voc = ContactsVocabulary.create_with_provider(key_value_provider)
        self.assertEquals(4, len(voc))

        self.assertEquals(
            ['<Term first-entry:First Entry>'], fterms(voc.search('fi en')))

        self.assertEquals(
            ['<Term first-entry:First Entry>'], fterms(voc.search('en fi')))

        self.assertEquals(
            ['<Term first-entry:First Entry>'], fterms(voc.search('rst')))

        # No fuzzy support:
        self.assertEquals([], fterms(voc.search('firt')))


        # Test custom vocabularies
        # ========================

        # See `opengever.ogds.base.vocabularies`

        # Lets set up some users and clients for testing the vocabularies with:
        session = create_session()

        # Users:

        _create_example_user(session, self.portal,
                                  'hugo.boss',
                                  {'firstname': 'Hugo',
                                   'lastname': 'Boss',
                                   'email': 'hugo@boss.local',
                                   'email2': 'hugo@private.ch'},
                                  ('client1_users',
                                   'client1_inbox_users'))

        _create_example_user(session, self.portal,
                                  'peter.muster',
                                  {'firstname': 'Peter',
                                   'lastname': 'Muster'},
                                  ('client2_users',
                                   'client2_inbox_users'))

        _create_example_user(session, self.portal,
                                  'hanspeter.linder',
                                  {'firstname': 'Hans-Peter',
                                   'lastname': 'Linder'},
                                  ('client2_users',
                                   'client2_inbox_users',
                                   'client1_users'))

        # Example of hidden users (``Robin Hood`` is everywhere but visible nowhere).

        _create_example_user(session, self.portal,
                                  'robin.hood',
                                  {'firstname': 'Robin',
                                   'lastname': 'Hood',
                                   'email': 'robin@hood.tld',
                                   'active': '0'},
                                  ('client1_users',
                                   'client1_inbox_users',
                                   'client2_users',
                                   'client2_inbox_users'))

        # Example of gone users (``hans.peter`` is nowwhere but still in the hidden terms).

        _create_example_user(session, self.portal,
                                  'hans.peter',
                                  {'firstname': 'Hans',
                                   'lastname': 'Peter',
                                   'email': 'hans.peter@peter.ch',
                                   'active': '0'},
                                   [])

        # Clients:

        _create_example_client(session, 'client1',
                                   {'title': 'Client 1',
                                    'ip_address': '127.0.0.1',
                                    'site_url': 'http://nohost/client1',
                                    'public_url': 'http://nohost/client1',
                                    'group': 'client1_users',
                                    'inbox_group': 'client1_inbox_users'})

        _create_example_client(session, 'client2',
                                   {'title': 'Client 2',
                                    'ip_address': '127.0.0.1',
                                    'site_url': 'http://nohost/client2',
                                    'public_url': 'http://nohost/client2',
                                    'group': 'client2_users',
                                    'inbox_group': 'client2_inbox_users'})

        _create_example_client(session, 'client3',
                                   {'title': 'Client 3',
                                    'enabled': False,
                                    'ip_address': '127.0.0.1',
                                    'site_url': 'http://nohost/client3',
                                    'public_url': 'http://nohost/client3',
                                    'group': 'client3_users',
                                    'inbox_group': 'client3_inbox_users'})


        # Lets set up some contacts:
        create_contacts(self.portal)


        # The current client is client1. Now let's login as hugo.boss for the tests.

        from plone.app.testing import login, logout
        logout()
        login(self.portal, 'hugo.boss')


        # Users vocabulary
        # ----------------

        # List all active users.

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.UsersVocabulary')

        voc = fact(self.portal)
        self.assertEquals(
            [u'<Term hugo.boss:Boss Hugo (hugo.boss)>',
             u'<Term peter.muster:Muster Peter (peter.muster)>',
             u'<Term hanspeter.linder:Linder Hans-Peter (hanspeter.linder)>'],
            fterms(list(voc)))


        # Hidden users are always accessible with ``getTerm`` or ``getTermByToken``, but
        # not visible in when listing vocabulary or searching it. And keep in mind
        # ``Robin Hood`` is always there.

        self.assertEquals(
            u'Hood Robin (robin.hood)', voc.getTerm('robin.hood').title)

        # Users and inboxes vocabulary
        # ----------------------------

        # Vocabulary of all users and all inboxes of a specific client. The client
        # is defined in the request either with key "client" or with key
        # "form.widgets.responsible_client".

        request.set('client', 'client2')
        setRequest(request)
        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.UsersAndInboxesVocabulary')
        voc = fact(self.portal)
        self.assertEquals(
            [u'<Term hanspeter.linder:Linder Hans-Peter (hanspeter.linder)>', u'<Term peter.muster:Muster Peter (peter.muster)>', u'<Term inbox:client2:Inbox: Client 2>'],
            fterms(list(voc)))

        request.set('client', 'client1')
        setRequest(request)
        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.UsersAndInboxesVocabulary')
        voc = fact(self.portal)
        self.assertEquals([u'<Term hanspeter.linder:Linder Hans-Peter (hanspeter.linder)>', u'<Term hugo.boss:Boss Hugo (hugo.boss)>', u'<Term inbox:client1:Inbox: Client 1>'], fterms(list(voc)))

        request.set('client', None)


        # All users and inboxes vocabulary
        # --------------------------------

        # The UsersAndInboxesVocabulary lists all users once per assigned client
        # and all inboxes.

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.AllUsersAndInboxesVocabulary')
        voc = fact(self.portal)

        self.assertEquals(
            [u'<Term client1:hanspeter.linder:Client 1: Linder Hans-Peter (hanspeter.linder)>',
             u'<Term client1:hugo.boss:Client 1: Boss Hugo (hugo.boss)>',
             u'<Term client1:inbox:client1:Inbox: Client 1>',
             u'<Term client2:hanspeter.linder:Client 2: Linder Hans-Peter (hanspeter.linder)>',
             u'<Term client2:peter.muster:Client 2: Muster Peter (peter.muster)>',
             u'<Term client2:inbox:client2:Inbox: Client 2>'],
            fterms(list(voc)))

        # Assigned users
        # --------------

        # Vocabulary of all users assigned to the current client.

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.AssignedUsersVocabulary')
        voc = fact(self.portal)

        self.assertEquals(
            [u'<Term hanspeter.linder:Linder Hans-Peter (hanspeter.linder)>',
             u'<Term hugo.boss:Boss Hugo (hugo.boss)>'],
            fterms(list(voc)))

        self.assertEquals([u'robin.hood', u'hans.peter'], voc.hidden_terms)

        self.assertIn(u'robin.hood', voc)

        # Contacts vocabulary
        # -------------------

        # Vocabulary of contacts.

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.ContactsVocabulary')
        voc = fact(self.portal)

        self.assertEquals(
            [u'<Term contact:kaufmann-sandra:Kaufmann Sandra (sandra.kaufmann@test.ch)>',
             u'<Term contact:kappeli-elisabeth:K\xe4ppeli Elisabeth (elisabeth.kaeppeli@test.ch)>',
             u'<Term contact:wermuth-roger:Wermuth Roger>'],
            fterms(list(voc)))

        # Contacts and users vocabulary
        # -----------------------------

        # Vocabulary of contacts and users.

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.ContactsAndUsersVocabulary')
        voc = fact(self.portal)
        self.assertEquals(
            [u'<Term hugo.boss:Boss Hugo (hugo.boss)>',
             u'<Term peter.muster:Muster Peter (peter.muster)>',
             u'<Term hanspeter.linder:Linder Hans-Peter (hanspeter.linder)>',
             u'<Term inbox:client1:Inbox: Client 1>',
             u'<Term inbox:client2:Inbox: Client 2>',
             u'<Term contact:kaufmann-sandra:Kaufmann Sandra (sandra.kaufmann@test.ch)>',
             u'<Term contact:kappeli-elisabeth:K\xe4ppeli Elisabeth (elisabeth.kaeppeli@test.ch)>',
             u'<Term contact:wermuth-roger:Wermuth Roger>'],
            fterms(list(voc)))

        # Email contacts and users vocabulary
        # -----------------------------------

        # Vocabulary containing all users and contacts with each e-mail
        # address they have.

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.EmailContactsAndUsersVocabulary')
        voc = fact(self.portal)

        self.assertEquals(
            [u'<Term hugo@boss.local:hugo.boss:Boss Hugo (hugo.boss, hugo@boss.local)>',
             u'<Term hugo@private.ch:hugo.boss:Boss Hugo (hugo.boss, hugo@private.ch)>',
             u'<Term robin@hood.tld:robin.hood:Hood Robin (robin.hood, robin@hood.tld)>',
             u'<Term hans.peter@peter.ch:hans.peter:Peter Hans (hans.peter, hans.peter@peter.ch)>',
             u'<Term sandra.kaufmann@test.ch:kaufmann-sandra:Kaufmann Sandra (sandra.kaufmann@test.ch)>',
             u'<Term elisabeth.kaeppeli@test.ch:kappeli-elisabeth:K\xe4ppeli Elisabeth (elisabeth.kaeppeli@test.ch)>'],
            fterms(list(voc)))

        # Clients vocabulary
        # ------------------

        # Vocabulary of all enabled clients (including the current one).

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.ClientsVocabulary')
        voc = fact(self.portal)
        self.assertEquals(
            [u'<Term client1:Client 1>', u'<Term client2:Client 2>'],
            fterms(list(voc)))

        # Assigned clients vocabulary
        # ---------------------------

        # Vocabulary of all assigned clients (=home clients) of the
        # current user, including the current client.

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.AssignedClientsVocabulary')
        voc = fact(self.portal)
        self.assertEquals([u'<Term client1:Client 1>'], fterms(list(voc)))

        logout()
        login(self.portal, 'peter.muster')

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.AssignedClientsVocabulary')
        voc = fact(self.portal)
        self.assertEquals([u'<Term client2:Client 2>'], fterms(list(voc)))

        logout()
        login(self.portal, 'hugo.boss')

        # Other Assigned clients vocabulary
        # ---------------------------------

        # Vocabulary of all assigned clients (=home clients) of the
        # current user. The current client is not included!

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.OtherAssignedClientsVocabulary')
        voc = fact(self.portal)

        self.assertEquals([], fterms(list(voc)))

        logout()
        login(self.portal, 'peter.muster')

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.OtherAssignedClientsVocabulary')
        voc = fact(self.portal)
        self.assertEquals([u'<Term client2:Client 2>'], fterms(list(voc)))

        logout()
        login(self.portal, 'hugo.boss')

        # Dossiers and documents vocabularies
        # ===================================

        # For the dossiers and documents vocabularies below we need to mock the communicator
        # because we don't want to set up another plone site to test that.


        class ClientCommunicatorMockUtility(communication.ClientCommunicator):
            implements(communication.IClientCommunicator)

            def get_open_dossiers(self, target_client_id):
                return [{'url': 'http://nohost/client2/op1/op2/dossier1',
                         'path': 'op1/op2/dossier1',
                         'title': 'Dossier 1',
                         'workflow_state': 'dossier-state-active',
                         'reference_number': 'OG 1.2 / 1'},
                        {'url': 'http://nohost/client2/op1/op2/dossier2',
                         'path': 'op1/op2/dossier2',
                         'title': 'Dossier 2',
                         'workflow_state': 'dossier-state-active',
                         'reference_number': 'OG 1.2 / 2'}]
                #
            def get_documents_of_dossier(self, target_client_id, dossier_path):
                dossier_url = 'http://nohost/client2/' + dossier_path
                return [{'path': dossier_path + '/document-1',
                         'url': dossier_url + '/document-1',
                         'title': 'First Document',
                         'review_state': 'draft'},
                        {'path': dossier_path + '/document-2',
                         'url': dossier_url + '/document-2',
                         'title': 'Second Document',
                         'review_state': 'draft'}]

        provideUtility(ClientCommunicatorMockUtility())


        # The tests below must be run by a user who is not assigned to the
        # current client (client1) but to another client (client2):

        logout()
        login(self.portal, 'peter.muster')

        # Home dossiers vocabulary
        # ------------------------

        request.set('client', 'client2')
        setRequest(request)
        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.HomeDossiersVocabulary')
        voc = fact(self.portal)

        self.assertEquals(
            [u'<Term op1/op2/dossier1:OG 1.2 / 1: Dossier 1>',
             u'<Term op1/op2/dossier2:OG 1.2 / 2: Dossier 2>'],
            fterms(list(voc)))

        request.set('client', None)


        # Documents in selected dossier vocabulary
        # ----------------------------------------

        request.set('client', 'client2')
        request.set('dossier_path', 'op1/op2/dossier2')
        setRequest(request)
        fact = getUtility(IVocabularyFactory,
                          name='opengever.ogds.base.DocumentInSelectedDossierVocabulary')
        voc = fact(self.portal)
        self.assertEquals(
            [u'<Term op1/op2/dossier2/document-1:First Document>',
             u'<Term op1/op2/dossier2/document-2:Second Document>'],
            fterms(list(voc)))

        request.set('client', None)
        request.set('dossier_path', None)
