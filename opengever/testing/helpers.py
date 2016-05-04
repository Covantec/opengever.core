from datetime import datetime
from opengever.base.date_time import as_utc
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.PloneLanguageTool.LanguageTool import LanguageBinding
import pytz
import transaction


DEFAULT_TZ = pytz.timezone('Europe/Zurich')


def localized_datetime(*args, **kwargs):
    """Localize timezone naive datetime to default timezone and return as utc.

    """
    if args or kwargs:
        dt = datetime(*args, **kwargs)
    else:
        dt = datetime.now()

    return as_utc(DEFAULT_TZ.localize(dt))


def create_plone_user(portal, userid, password='demo09'):
    acl_users = getToolByName(portal, 'acl_users')
    acl_users.source_users.addUser(userid, userid, password)


def obj2brain(obj, unrestricted=False):
    catalog = getToolByName(obj, 'portal_catalog')
    query = {'path': {'query': '/'.join(obj.getPhysicalPath()), 'depth': 0}}

    if unrestricted:
        brains = catalog.unrestrictedSearchResults(query)
    else:
        brains = catalog(query)

    if len(brains) == 0:
        raise Exception('Not in catalog: %s' % obj)

    return brains[0]


def index_data_for(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    return catalog.getIndexDataForRID(obj2brain(obj).getRID())


def set_preferred_language(request, code):
    binding = LanguageBinding(api.portal.get_tool('portal_languages'))
    binding.DEFAULT_LANGUAGE = code
    binding.LANGUAGE = code
    request['LANGUAGE_TOOL'] = binding


def add_languages(codes, support_combined=True):
    lang_tool = api.portal.get_tool('portal_languages')
    if support_combined:
        lang_tool.use_combined_language_codes = True

    for code in codes:
        lang_tool.addSupportedLanguage(code)

    transaction.commit()

def obj2paths(objs):
    """Returns a list of paths(string) for the given objects
    """
    return ['/'.join(obj.getPhysicalPath()) for obj in objs]
