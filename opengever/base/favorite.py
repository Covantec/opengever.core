from opengever.base.browser.helper import get_css_class
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from plone.uuid.interfaces import IUUID
from sqlalchemy import and_
from zExceptions import NotFound


class FavoriteManager(object):

    def delete(self, userid, fav_id):
        favorite = Favorite.query.get(fav_id)

        if not favorite:
            raise NotFound(
                u'Favorite with the id {} does not exist.'.format(fav_id))

        if userid != favorite.userid:
            raise NotFound(
                u'Parameter mismatch: Favorite {} is not owned by {}'.format(
                    fav_id, userid))

        create_session().delete(favorite)

    def add(self, userid, obj):
        favorite = Favorite(
            userid=userid,
            oguid=Oguid.for_object(obj),
            title=obj.title,
            portal_type=obj.portal_type,
            icon_class=get_css_class(obj),
            plone_uid=IUUID(obj),
            position=self.get_next_position(userid))

        create_session().add(favorite)
        create_session().flush()
        return favorite

    def get_next_position(self, userid):
        position = Favorite.query.get_highest_position(userid)
        if not position:
            return 0

        return position + 1

    def update(self, userid, fav_id, title, position):
        favorite = Favorite.query.get(fav_id)

        if not favorite:
            raise NotFound(
                u'Favorite with the id {} does not exist.'.format(fav_id))

        if userid != favorite.userid:
            raise NotFound(
                u'Parameter mismatch: Favorite {} is not owned by {}'.format(
                    fav_id, userid))

        if title:
            favorite.title = title
            favorite.is_title_personalized = True

        if position:
            self.update_position(favorite, position, userid)

        return favorite

    def update_position(self, fav_to_updated, position, userid):
        """Update the position all favorites affected by the reordering."""

        old_position = fav_to_updated.position
        favorites_to_raise = Favorite.query.by_userid(userid).filter(
            and_(Favorite.position >= position, Favorite.position < old_position))

        for favorite in favorites_to_raise:
            favorite.position = favorite.position + 1

        fav_to_updated.position = position

    def list_all(self, userid):
        return Favorite.query.by_userid(userid=userid).all()
