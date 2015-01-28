import argparse
import os
import csv

from corpustools.corpus.io import load_binary
from corpustools.mutualinfo.mutual_information import *


def main():

    #### Parse command-line arguments
    parser = argparse.ArgumentParser(description = \
             'Phonological CorpusTools: mutual information CL interface')
    parser.add_argument('corpus_file_name', help='Name of corpus file')
    parser.add_argument('query', help='bigram, as str separated by comma')
    parser.add_argument('-s', '--sequence_type', default='transcription', help="The attribute of Words to calculate FL over. Normally this will be the transcription, but it can also be the spelling or a user-specified tier.")
    parser.add_argument('-o', '--outfile', help='Name of output file')

    args = parser.parse_args()

    ####

    corpus = load_binary(args.corpus_file_name)

    query = tuple(args.query.split(','))
    if len(query) < 2:
        print('Warning! Your queried bigram could not be processed. Please separate the two segments with a comma, as in the call: pct_mutualinfo example.corpus m,a')

    result = pointwise_mi(corpus, query, args.sequence_type)

    if args.outfile:
        with open(args.outfile, 'w') as outfile:
            outfile.write(str(result)) # TODO: develop output file structure
    else:
        print('No output file name provided.')
        print('The mutual information of the given inputs is {}.'.format(str(result)))


if __name__ == '__main__':
    main()
