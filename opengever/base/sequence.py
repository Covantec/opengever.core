from five import grok
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, getAdapter
from zope.interface import Interface

from Products.CMFCore.interfaces import ISiteRoot
from Products.Transience.Transience import Increaser
from plone.dexterity.interfaces import IDexterityContent

from opengever.dossier.behaviors.dossier import IDossierMarker

SEQUENCE_NUMBER_ANNOTATION_KEY = 'ISequenceNumber.sequence_number'


class ISequenceNumber(Interface):
    """  The sequence number utility provides a getNumber(obj) method
    which returns a unique number for each object.
    """

    def get_number(self, obj):
        """ Returns the sequence number for the given *obj*
        """


class SequenceNumber(grok.GlobalUtility):
    """ The sequence number utility provides a getNumber(obj) method
    which returns a unique number for each object.
    """
    grok.provides(ISequenceNumber)

    def get_number(self, obj):
        ann = IAnnotations(obj)
        if SEQUENCE_NUMBER_ANNOTATION_KEY not in ann.keys():
            generator = getAdapter(obj, ISequenceNumberGenerator)
            value = generator.generate()
            ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = value
        return ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY)
    
 
class ISequenceNumberGenerator(Interface):
    """ The sequence number generator adapter generates a new sequence number
    for the adapted object
    """

    def generate(self):
        """ Returns a new sequence number for the adapted object
        """

 
class DefaultSequenceNumberGenerator(grok.Adapter):
    """ Provides a default sequence number generator. The portal_type of the object
    is used as *unique-key*
    For choosing the number the Products.Transience.Transience.Increaser should be
    used. See:
    http://pyyou.wordpress.com/2009/12/09/how-to-add-a-counter-without-conflict-error-in-zope/
    """
    grok.provides(ISequenceNumberGenerator)
    grok.context(IDexterityContent)

    def generate(self):
        return self.get_next(self.key)

    @property
    def key(self):
        return u'DefaultSequenceNumberGenerator.%s' % self.context.portal_type

    def get_next(self, key):
        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        if SEQUENCE_NUMBER_ANNOTATION_KEY not in ann.keys():
            ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = PersistentDict()
        map = ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY)
        if key not in map:
            map[key] = Increaser(0)
        # increase
        inc = map[key]
        inc.set(inc()+1)
        map[key] = inc
        return inc()

 
class DossierSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All dossier-types should use the same range/key of sequence numbers.
    """
    grok.provides(ISequenceNumberGenerator)
    grok.context(IDossierMarker)

    key = 'DossierSequenceNumberGenerator'
