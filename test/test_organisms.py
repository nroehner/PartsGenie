'''
PartsGenie (c) University of Liverpool 2020

All rights reserved.

@author:  neilswainston
'''
import unittest

import organisms


class Test(unittest.TestCase):
    '''Test class for organisms module.'''

    def test_get_organisms(self):
        '''Tests get_organisms first time, generating cached file.'''
        self.__test_get_organisms(2)

    def test_get_organisms_cached(self):
        '''Tests get_organisms second time, using cached file.'''
        self.__test_get_organisms(2)

    def __test_get_organisms(self, parent_id):
        '''Tests submit method.'''
        orgs = organisms.get_organisms(parent_id)

        self.assertTrue(len(orgs), 32863)
        self.assertIn('Escherichia coli', orgs)
        self.assertIsInstance(orgs['Escherichia coli'], str)


if __name__ == '__main__':
    unittest.main()
