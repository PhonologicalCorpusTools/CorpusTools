import argparse
import os
import csv
import re
import sys

# default to importing from CorpusTools repo
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0,base)

from corpustools.corpus.io import load_binary
from corpustools.corpus.classes.lexicon import EnvironmentFilter
from corpustools.phonosearch.phonosearch import phonological_search

def main():

    #### Parse command-line arguments
    parser = argparse.ArgumentParser(description = \
             'Phonological CorpusTools: phonological search CL interface')
    parser.add_argument('corpus_file_name', help='Name of corpus file')
    parser.add_argument('sequence', 
        help=('Sequence to search for, with segment positions separated by commas,'
        +' and with sets separated by slashes.'
        +' E.g. the input i will return all words with the segment [i], while'
        +' the input a/o,t/p,i,n will return all words with [atin], [apin],'
        +' [otin], or [opin].'))
    parser.add_argument('-s', '--sequence_type', default='transcription', 
        help="The attribute of Words to search within. Normally this will be the transcription, but it can also be the spelling or a user-specified tier.")
    parser.add_argument('-o', '--outfile', help='Name of output file')

    args = parser.parse_args()

    ####

    try:
        home = os.path.expanduser('~')
        corpus = load_binary(os.path.join(home, 'Documents', 'PCT', 'CorpusTools', 'CORPUS', args.corpus_file_name))
    except FileNotFoundError:
        corpus = load_binary(args.corpus_file_name)

    split_sequence = [tuple(pos.split('/')) for pos in args.sequence.split(',')]
    middle = split_sequence[0]
    try:
        rhs = split_sequence[1:]
    except:
        rhs = None
    if len(rhs) == 0:
        rhs = None

    ef = EnvironmentFilter(middle, None, rhs)

    results = phonological_search(corpus, [ef], sequence_type=args.sequence_type)

    if args.outfile:
        with open(args.outfile, 'w') as outfile:
            for result in results:
                outfile.write(' '.join(getattr(result[0], args.sequence_type))+'\n')
        print('Search results written to output file.')
    else:
        print('No output file name provided.')
        print('Your search produced the results below:')
        for result in results:
            print('{}'.format(result[0]))
        print('Total number of results: {}'.format(str(len(results))))
        print('Please specify an output file name with -o to save these results.')


if __name__ == '__main__':
    main()
