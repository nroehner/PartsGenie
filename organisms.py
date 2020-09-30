'''
PartsGenie (c) University of Liverpool 2020

All rights reserved.

@author:  neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order
import os.path

from genegeniebio.utils import codon_utils, ncbi_tax_utils
import pandas as pd


def get_organisms(parent_id):
    '''Get all valid organisms (bacterial with codon usage tables).'''
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(curr_dir, '%s.csv' % parent_id)

    if not os.path.exists(filepath):
        organisms = codon_utils.get_codon_usage_organisms(expand=True)
        ids = ncbi_tax_utils.TaxonomyFactory().get_child_ids(parent_id)
        valid_ids = set(organisms.values()).intersection(set(ids))

        valid_organisms = {name: tax_id for name, tax_id in organisms.items()
                           if tax_id in valid_ids}

        _write(valid_organisms, filepath)

        return valid_organisms

    return _read(filepath)


def _write(organisms, filepath):
    '''Write organisms.'''
    df = pd.Series(organisms, name='id')
    df.index.name = 'name'
    df.to_csv(filepath)


def _read(filepath):
    '''Read organisms.'''
    df = pd.read_csv(filepath, dtype=str)
    return pd.Series(df['id'].values, index=df['name']).to_dict()
