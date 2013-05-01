import os
import unittest2 as unittest
import doctest
from opengever.mail.testing import OPENGEVER_MAIL_INTEGRATION_TESTING
from plone.testing import layered


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


HERE = os.path.dirname(os.path.abspath(__file__))


def test_suite():

    suite = unittest.TestSuite()

    txtfiles = [f for f in os.listdir(HERE)
                if f.endswith('.txt') and
                not f.startswith('.')]


    for testfile in txtfiles:
            suite.addTests([
                  layered(doctest.DocFileSuite(testfile,
                                               optionflags=OPTIONFLAGS),
                          layer=OPENGEVER_MAIL_INTEGRATION_TESTING),
              ])

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
