from opengever.activity.model import NotificationDefault
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.base.model import create_session
from sqlalchemy.orm.exc import NoResultFound


DEFAULT_SETTINGS = [
    {'kind': 'task-added',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE],
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE]},
    {'kind': 'task-transition-cancelled-open',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-delegate',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-in-progress-resolved',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-in-progress-tested-and-closed',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-modify-deadline',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-cancelled',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-in-progress',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-rejected',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-resolved',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-tested-and-closed',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-commented',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-reassign',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE],
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE]},
    {'kind': 'task-transition-rejected-open',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-resolved-in-progress',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-resolved-tested-and-closed',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-added',
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE],
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-accept',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-assign-to-dossier',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-close',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-reassign',
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE],
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-reassign-refused',
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE],
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-refuse', 'mail_notification': False,
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
]


def insert_notification_defaults(site):
    session = create_session()
    for item in DEFAULT_SETTINGS:
        try:
            setting = NotificationDefault.query.by_kind(item.get('kind')).one()
        except NoResultFound:
            setting = NotificationDefault(kind=item.get('kind'))
            session.add(setting)

        setattr(setting, 'mail_notification_roles',
                item.get('mail_notification_roles', []))
        setattr(setting, 'badge_notification_roles',
                item.get('badge_notification_roles', []))
