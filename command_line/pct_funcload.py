import argparse
import os
import csv

from corpustools.corpus.io import load_binary
from corpustools.funcload.functional_load import *

#### Parse command-line arguments
parser = argparse.ArgumentParser(description = \
         'Phonological CorpusTools: functional load CL interface')
parser.add_argument('corpus_file_name', help='Name of corpus file')
parser.add_argument('segment_pairs_file_name', help='Name of file with segment pairs')
parser.add_argument('-o', '--outfile', help='Name of output file')

args = parser.parse_args()


#### Script-specific functions

def read_segment_pairs(spfile):
    text = spfile.read().strip()
    return 


####

with open(args.segment_pairs_file_name) as segpairs_file:
    corpus = load_binary(args.corpus_file_name)[0]
    segpairs = [line for line in csv.reader(segpairs_file, delimiter='\t') if len(line) > 0]

    result = minpair_fl(corpus, segpairs)

with open(args.outfile, 'w') as outfile:
    outfile.write(result) # <- attention here