'''
PartsGenie (c) GeneGenie Bioinformatics Ltd. 2020

All rights reserved.

@author:  neilswainston
'''
import unittest

import organisms


class Test(unittest.TestCase):
    '''Test class for organisms module.'''

    def test_get_organisms(self):
        '''Tests get_organisms first time, generating cached file.'''
        self.__test_get_organisms()

    def test_get_organisms_cached(self):
        '''Tests get_organisms second time, using cached file.'''
        self.__test_get_organisms()

    def __test_get_organisms(self):
        '''Tests submit method.'''
        orgs = organisms.get_organisms()

        self.assertTrue(len(orgs), 32863)
        self.assertIn('Escherichia coli', orgs)
        self.assertIsInstance(orgs['Escherichia coli'], str)


if __name__ == '__main__':
    unittest.main()
