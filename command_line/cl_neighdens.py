import argparse
import os
import csv

from corpustools.corpus.io import load_binary
from corpustools.neighdens.neighborhood_density import neighborhood_density

#### Parse command-line arguments
parser = argparse.ArgumentParser(description = \
         'Phonological CorpusTools: neighborhood density CL interface')
parser.add_argument('corpus_file_name', help='Name of corpus file')
parser.add_argument('query', help='Name of word to query')
# more needed
parser.add_argument('-o', '--outfile', help='Name of output file')

args = parser.parse_args()


#### Script-specific functions

def read_segment_pairs(spfile):
    text = spfile.read().strip()
    return 


####

corpus = load_binary(args.corpus_file_name)
print(type(corpus))
print(len(corpus[0])) # !?!?!?!?!?!
print(neighborhood_density(corpus[0], args.query))