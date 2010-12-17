import doctest
from plone.testing import layered
import unittest2 as unittest
from opengever.advancedsearch.testing import OPENGEVER_ADV_SEARCH_TESTING


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


TESTFILES = (
    'search.txt',
    )



def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(doctest.DocFileSuite(filename,
                                                 optionflags=OPTIONFLAGS),
                    layer=OPENGEVER_ADV_SEARCH_TESTING)
                    for filename in TESTFILES])
    return suite
