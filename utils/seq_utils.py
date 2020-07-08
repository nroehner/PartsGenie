'''
PartsGenie (c) GeneGenie Bioinformatics Ltd. 2020

All rights reserved.

@author:  neilswainston
'''
# pylint: disable=too-many-arguments
from collections import defaultdict
import itertools

import random
import re
from subprocess import call
import tempfile

from Bio import Seq, SeqIO, SeqRecord
from Bio.Blast import NCBIXML
from Bio.Data import CodonTable
from Bio.Restriction import Restriction, Restriction_Dictionary
from Bio.SeqUtils.MeltingTemp import Tm_NN


NUCLEOTIDES = ['A', 'C', 'G', 'T']

AA_CODES = {'Ala': 'A',
            'Cys': 'C',
            'Asp': 'D',
            'Glu': 'E',
            'Phe': 'F',
            'Gly': 'G',
            'His': 'H',
            'Ile': 'I',
            'Lys': 'K',
            'Leu': 'L',
            'Met': 'M',
            'Asn': 'N',
            'Pro': 'P',
            'Gln': 'Q',
            'Arg': 'R',
            'Ser': 'S',
            'Thr': 'T',
            'Val': 'V',
            'Trp': 'W',
            'Tyr': 'Y',
            'Stop': '*'}


NA = 'NA'
K = 'K'
TRIS = 'TRIS'
MG = 'MG'
DNTP = 'DNTP'

__DEFAULT_REAG_CONC = {NA: 0.05, K: 0, TRIS: 0, MG: 0.01, DNTP: 0}

AA_COD = defaultdict(list)

for cod, am_ac in \
        CodonTable.unambiguous_dna_by_name['Standard'].forward_table.items():
    AA_COD[am_ac].append(cod)

# ssl._create_default_https_context = ssl._create_unverified_context


def find_invalid(seq, max_repeat_nuc=float('inf'), restr_enzyms=None):
    '''Finds invalid sequences.'''
    inv = []
    seq = seq.upper()

    # Invalid repeating nucleotides:
    if max_repeat_nuc != float('inf'):
        pattern = [''.join([nucl] * (max_repeat_nuc + 1))
                   for nucl in NUCLEOTIDES]
        pattern = re.compile(r'(?=(' + '|'.join(pattern) + '))')

        inv = [m.start() for m in pattern.finditer(seq)]

    # Invalid restriction sites:
    if restr_enzyms:
        for rest_enz in [_get_restr_type(name) for name in restr_enzyms]:
            inv.extend(rest_enz.search(Seq.Seq(seq)))

    return inv


def is_invalid(seq, max_repeat_nuc=float('inf'), restr_enzyms=None):
    '''Checks whether a sequence is valid.'''
    return len(find_invalid(seq, max_repeat_nuc, restr_enzyms)) > 0


def get_all_rev_trans(aa_seq):
    '''Returns all reverse translations of amino acid sequence.'''
    codons = [AA_COD[aa] for aa in aa_seq.strip()]
    return [''.join(t) for t in list(itertools.product(*codons))]


def get_random_dna(length, max_repeat_nuc=float('inf'), restr_enzyms=None):
    '''Returns a random sequence of DNA of the supplied length,
    while adhering to a maximum number of repeating nucleotides.'''
    max_attempts = 100
    attempts = 0
    len_add = 16

    seq = ''

    while True:
        attempts += 1

        if attempts > max_attempts:
            raise ValueError('Unable to optimise sequence.')

        while len(seq) < length:
            seq += _get_random_dna(len_add)

            if is_invalid(seq, max_repeat_nuc, restr_enzyms):
                seq = seq[:-len_add]

        if not is_invalid(seq, max_repeat_nuc, restr_enzyms):
            return seq[:length]

    return None


def mutate_seq(seq, mutations=1, alphabet=None):
    '''Mutates sequence.'''
    if alphabet is None:
        alphabet = NUCLEOTIDES

    seq_new = seq

    for _ in range(mutations):
        move = random.random()
        pos = int(random.random() * len(seq))
        base = random.choice(alphabet)

        # Insert:
        if move < 0.1:
            seq_new = seq_new[1:pos + 1] + base + seq_new[pos + 1:]

        # Delete:
        elif move < 0.2:
            seq_new = base + seq_new[:pos] + seq_new[pos + 1:]

        # Replace:
        else:
            seq_new = seq_new[:pos] + base + seq_new[pos + 1:]

    return seq_new


def get_melting_temp(dna1, dna2=None, reag_concs=None, strict=True):
    '''Calculates melting temperarure of DNA sequence against its
    complement, or against second DNA sequence using Nearest-Neighbour
    method.'''
    assert len(dna1) > 1

    reagent_concs = __DEFAULT_REAG_CONC

    if reag_concs is not None:
        reagent_concs.update(reag_concs)

    reagent_conc = {k: v * 1000 for k, v in reagent_concs.items()}
    dnac1 = 30

    return Tm_NN(dna1, check=True, strict=strict, c_seq=dna2, shift=0,
                 Na=reagent_conc[NA], K=reagent_conc[K],
                 Tris=reagent_conc[TRIS], Mg=reagent_conc[MG],
                 dNTPs=reagent_conc[DNTP],
                 dnac1=dnac1, dnac2=dnac1, selfcomp=dna2 is None,
                 saltcorr=7)


def get_seq_by_melt_temp(seq, target_melt_temp, forward=True,
                         terminii=None,
                         reagent_concs=None,
                         tol=0.025):
    '''Returns a subsequence close to desired melting temperature.'''
    if terminii is None:
        terminii = ['A', 'C', 'G', 'T']
    else:
        terminii = [term.upper() for term in terminii]

    best_delta_tm = float('inf')
    best_subseq = ''
    best_melt_temp = float('NaN')
    in_tol = False

    for i in range(3, len(seq)):
        subseq = seq[:(i + 1)] if forward else seq[-(i + 1):]
        melt_temp = get_melting_temp(subseq, None, reagent_concs)

        if subseq[-1 if forward else 0].upper() in terminii:
            delta_tm = abs(melt_temp - target_melt_temp)

            if delta_tm / target_melt_temp < tol:
                in_tol = True

                if delta_tm < best_delta_tm:
                    best_delta_tm = delta_tm
                    best_subseq = subseq
                    best_melt_temp = melt_temp
            elif in_tol:
                break

    if in_tol:
        return best_subseq, best_melt_temp

    raise ValueError('Unable to get sequence of required melting temperature')


def get_rand_seq_by_melt_temp(target_melt_temp,
                              max_repeat_nuc=float('inf'),
                              restr_enzyms=None,
                              reagent_concs=None,
                              tol=0.025):
    '''Returns a random close to desired melting temperature.'''
    seq = random.choice(NUCLEOTIDES)

    while True:
        seq += random.choice(NUCLEOTIDES)

        if is_invalid(seq, max_repeat_nuc, restr_enzyms):
            seq = random.choice(NUCLEOTIDES)
            continue

        melt_temp = get_melting_temp(seq, None, reagent_concs)

        delta_tm = abs(melt_temp - target_melt_temp)

        if delta_tm / target_melt_temp < tol:
            return seq, melt_temp

    raise ValueError('Unable to get sequence of required melting temperature')


def do_blast(id_seqs_subjects, id_seqs_queries, program='blastn',
             dbtype='nucl', evalue=1.0, word_size=28):
    '''Performs BLAST of query sequences against subject sequences.'''
    db_filename = write_fasta(id_seqs_subjects)
    query_filename = write_fasta(id_seqs_queries)
    result_file = tempfile.NamedTemporaryFile(prefix='blast_result_',
                                              suffix='.xml',
                                              delete=False)
    log_file = tempfile.NamedTemporaryFile(prefix='makeblastdb_log',
                                           suffix='.txt',
                                           delete=False)

    call(['makeblastdb',
          '-in', db_filename,
          '-out', db_filename,
          '-dbtype', dbtype,
          '-logfile', log_file.name])

    call([program,
          '-query', query_filename,
          '-db', db_filename,
          '-out', result_file.name,
          '-evalue', str(evalue),
          '-word_size', str(word_size),
          '-outfmt', '5'])

    return NCBIXML.parse(open(result_file.name))


def do_clustal(in_data, is_fasta_file=False, result_file=None,
               guidetree_file=None):
    '''Performs Clustal Omega multiple sequence alignment.'''
    result_file = tempfile.NamedTemporaryFile(prefix='clustalo_result_',
                                              suffix='.fasta',
                                              delete=False).name \
        if result_file is None \
        else result_file

    guidetree_file = tempfile.NamedTemporaryFile(prefix='clustalo_tree_',
                                                 suffix='.dnd',
                                                 delete=False).name \
        if guidetree_file is None \
        else guidetree_file

    call(['clustalo',
          '-i', in_data if is_fasta_file else write_fasta(in_data),
          '-o', result_file,
          '--guidetree-out=' + guidetree_file,
          '--force'])

    return read_fasta(result_file)


def read_fasta(filename):
    '''Reads a fasta file.'''
    with open(filename, 'rU') as fle:
        seqs = {record.id: str(record.seq)
                for record in SeqIO.parse(fle, 'fasta')}

    return seqs


def write_fasta(id_seqs, filename=None):
    '''Writes a fasta file.'''
    if filename is None:
        temp_file = tempfile.NamedTemporaryFile(prefix='fasta_', suffix='.txt',
                                                delete=False)
        filename = temp_file.name

    records = [SeqRecord.SeqRecord(Seq.Seq(seq), str(seq_id), '', '')
               for seq_id, seq in id_seqs.items()]

    SeqIO.write(records, filename, 'fasta')

    return filename


def pcr(seq, forward_primer, reverse_primer):
    '''Apply in silico PCR.'''
    for_primer_pos = seq.find(forward_primer.upper())

    rev_primer_pos = \
        seq.find(str(Seq.Seq(reverse_primer).reverse_complement().upper()))

    if for_primer_pos > -1 and rev_primer_pos > -1:
        seq = seq[for_primer_pos:] + \
            seq[:rev_primer_pos + len(reverse_primer)]
    elif for_primer_pos > -1:
        seq = seq[for_primer_pos:]
    elif rev_primer_pos > -1:
        seq = seq[:rev_primer_pos + len(reverse_primer)]

    return seq, for_primer_pos


def _get_random_dna(length):
    '''Returns a random sequence of DNA of the supplied length.'''
    return ''.join(random.choice(['A', 'C', 'G', 'T']) for _ in range(length))


def _get_restr_type(name):
    '''Gets RestrictionType from name.'''
    types = [
        x for _, (x, y) in Restriction_Dictionary.typedict.items()
        if name in y][0]

    enz_types = tuple(getattr(Restriction, typ)
                      for typ in types)

    return Restriction.RestrictionType(
        str(name), enz_types, Restriction_Dictionary.rest_dict[name])
