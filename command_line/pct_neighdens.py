import argparse
import os
import csv

from corpustools.corpus.io.binary import load_binary
from corpustools.neighdens.neighborhood_density import neighborhood_density


#### Parse command-line arguments
parser = argparse.ArgumentParser(description = \
         'Phonological CorpusTools: neighborhood density CL interface')
parser.add_argument('corpus_file_name', help='Name of corpus file')
parser.add_argument('query', help='Name of word to query')
parser.add_argument('-s', '--string_type', default = 'transcription', help="If 'spelling', will calculate neighborhood density on spelling. If 'transcription' will calculate neighborhood density on transcriptions.")
algorithm = 'edit_distance'
max_distance = 1
tiername = 'transcription'
count_what='type'
parser.add_argument('-o', '--outfile', help='Name of output file')

args = parser.parse_args()


####

corpus = load_binary(args.corpus_file_name)[0]

print(neighborhood_density(corpus, args.query))