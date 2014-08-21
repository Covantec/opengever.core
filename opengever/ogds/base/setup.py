from ftw.dictstorage.sql import DictStorageModel
from opengever.ogds.base.utils import create_session
from opengever.ogds.models import BASE
from opengever.ogds.models.client import Client
from opengever.ogds.models.group import Group
from z3c.saconfig.interfaces import IScopedSession
from zope.component import queryUtility


def create_sql_tables():
    """Creates the sql tables for the models.
    """
    if not queryUtility(IScopedSession, 'opengever'):
        return

    session = create_session()
    BASE.metadata.create_all(session.bind)

    DictStorageModel.metadata.create_all(session.bind)


def create_example_client(session, client_id, properties):
    if len(session.query(Client).filter_by(client_id=client_id).all()) == 0:
        #create users_group if not exist
        temp = session.query(Group).filter(
            Group.groupid == properties.get('group')).all()
        if len(temp) == 0:
            users_group = Group(properties.get('group'))
        else:
            users_group = temp[0]
        properties.pop('group')

        #create inbox_group if not exist
        temp = session.query(Group).filter(
            Group.groupid == properties.get('inbox_group')).all()
        if len(temp) == 0:
            inbox_group = Group(properties.get('inbox_group'))
        else:
            inbox_group = temp[0]
        properties.pop('inbox_group')

        client = Client(client_id, **properties)
        client.users_group = users_group
        client.inbox_group = inbox_group
        session.add(client)
        return client
