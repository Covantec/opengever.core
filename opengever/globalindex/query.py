from opengever.globalindex import Session
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.globalindex.oguid import Oguid
from sqlalchemy.sql.expression import asc, desc
from zope.deprecation import deprecated
from zope.interface import implements


class TaskQuery(object):
    """A global utility for querying opengever tasks.
    """
    implements(ITaskQuery)

    def get_tasks_by_paths(self, task_paths):
        """Returns a set of tasks whos pahts are listed in `paths`.
        """
        return Session().query(Task).filter(
            Task.physical_path.in_(task_paths)).all()

    def _get_tasks_for_issuer_query(self, issuer, sort_on='modified',
                                    sort_order='reverse'):
        """Returns a sqlachemy query of all tasks issued by the given issuer.
        """

        sort_on = getattr(Task, sort_on)
        if sort_order == 'reverse':
            return Session().query(Task).filter(Task.issuer == issuer
                                                ).order_by(desc(sort_on))
        else:
            return Session().query(Task).filter(Task.issuer == issuer
                                                ).order_by(asc(sort_on))

    def get_tasks_for_issuer(self, issuer, sort_on='modified',
                             sort_order='reverse'):
        """Returns all tasks issued by the given issuer.
        """

        return self._get_tasks_for_issuer_query(
            issuer, sort_on=sort_on, sort_order=sort_order).all()

    def get_tasks_for_client(self, client, sort_on='modified'):
        """Return a sqlachemy query of all task on the specified client.
        """

        sort_on = getattr(Task, sort_on)
        return Session().query(Task).filter(Task.client_id == client
                                            ).order_by(asc(sort_on)).all()

    def _get_tasks_for_assigned_client_query(self, client, sort_on='modified',
                                             sort_order='reverse'):
        """Return a sqlachemy query of all task assigned to the actual client.
        """

        sort_on = getattr(Task, sort_on)
        if sort_order == 'reverse':
            return Session().query(Task).filter(Task.assigned_client == client
                                                ).order_by(desc(sort_on))
        else:
            return Session().query(Task).filter(Task.assigned_client == client
                                                ).order_by(asc(sort_on))

    def get_tasks_for_assigned_client(self, client, sort_on='modified',
                                     sort_order='reverse'):
        """Return all task assigned to the actual client.
        """

        return self._get_tasks_for_assigned_client_query(
            client, sort_on=sort_on, sort_order=sort_order).all()

    get_task_for_assigned_client = get_tasks_for_assigned_client
    deprecated(get_task_for_assigned_client,
               'Use get_tasks_for_assigned_client instead of '
               'get_task_for_assigned_client (plural).')
