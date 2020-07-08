'''
PartsGenie (c) GeneGenie Bioinformatics Ltd. 2020

All rights reserved.

@author:  neilswainston
'''
import random
import unittest

from utils import seq_utils


class Test(unittest.TestCase):
    '''Test class for seq_utils.'''

    def test_get_all_rev_trans(self):
        '''Tests get_all_rev_trans method.'''
        aa_seq = 'LS'
        rev_trans = seq_utils.get_all_rev_trans(aa_seq)
        self.assertEqual(len(rev_trans), 36)

    def test_find_invalid(self):
        '''Tests find_invalid method.'''
        seq = 'ggtctaaaaatttttttaaaaaccagagtttttt'

        self.assertEqual(seq_utils.find_invalid(seq, 5, ['BsaI']),
                         [10, 11, 28])

    def test_is_invalid(self):
        '''Tests is_invalid method.'''
        seq_inv = 'ggtctaaaaatttttttaaaaaccagagtttttt'
        self.assertTrue(seq_utils.is_invalid(seq_inv, 5, ['BsaI']))

        seq_val = 'ggtctaaaa'
        self.assertFalse(seq_utils.is_invalid(seq_val, 5, ['BsaI']))

    def test_get_random_dna(self):
        '''Tests get_random_dna method.'''
        lngth = random.randint(1000, 10000)
        self.assertEqual(lngth,
                         len(seq_utils.get_random_dna(lngth, 4, ['BsaI'])))

    def test_get_seq_by_melt_temp(self):
        '''Tests get_seq_by_melt_temp method.'''
        seq, _ = seq_utils.get_seq_by_melt_temp('agcgtgcgaagcgtgcgatcctcc', 70)
        self.assertEqual(seq, 'agcgtgcgaagcgtgcgatc')

    def test_get_rand_seq_by_melt_temp(self):
        '''Tests get_rand_seq_by_melt_temp method.'''
        target_temp = random.randint(50, 100)
        _, temp = seq_utils.get_rand_seq_by_melt_temp(target_temp, 4, ['BsaI'])
        self.assertTrue(abs(target_temp - temp) / target_temp < 0.025)

    def test_do_blast(self):
        '''Tests do_blast method.'''
        id_seq = {'test': seq_utils.get_random_dna(1024)}
        results = seq_utils.do_blast(id_seq, id_seq, evalue=10, word_size=4)

        alignments = []

        for result in results:
            for alignment in result.alignments:
                for hsp in alignment.hsps:
                    alignments.append(hsp)
                    print(hsp)

        self.assertGreater(len(alignments), 1)


if __name__ == "__main__":
    unittest.main()
