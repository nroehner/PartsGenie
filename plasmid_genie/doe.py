'''
PartsGenie (c) GeneGenie Bioinformatics Ltd. 2020

All rights reserved.

@author:  neilswainston
'''


def get_designs(filename):
    '''Reads design file from DOE.'''
    designs = []
    with open(filename) as designfile:
        for line in designfile.read().split('\r'):
            tokens = line.split()
            designs.append({'design': tokens + [tokens[0]]})
    return designs
