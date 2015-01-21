import argparse
import os
import csv
import re
import sys

from corpustools.corpus.io import load_binary

def main():

    #### Parse command-line arguments
    parser = argparse.ArgumentParser(description = \
             'Phonological CorpusTools: phonological search CL interface')
    parser.add_argument('corpus_file_name', help='Name of corpus file')
    parser.add_argument('seg_list', help='Segments to search for, separated by commas')
    parser.add_argument('-e', '--environments', help='Environments in which to search for the segments, written using _ (underscore) notation and separated by commas')
    parser.add_argument('-s', '--sequence_type', default='transcription', help="The attribute of Words to search within. Normally this will be the transcription, but it can also be the spelling or a user-specified tier.")
    parser.add_argument('-o', '--outfile', help='Name of output file')

    # fix for argparse's inability to take optional arguments beginning with -
    for i, arg in enumerate(sys.argv):
        if arg == '-e':
            sys.argv[i] = '-e{}'.format(sys.argv[i+1])
            sys.argv[i+1] = ''
    sys.argv = [arg for arg in sys.argv if arg != '']

    args = parser.parse_args()

    ####

    corpus = load_binary(args.corpus_file_name)[0]

    segments = args.seg_list.split(',')
    if args.environments:
        args.environments = re.split(',(?!^|\+|\-|0|\.|1)', args.environments)

    results = corpus.phonological_search(segments, envs=args.environments, sequence_type=args.sequence_type)

    if args.outfile:
        with open(args.outfile, 'w') as outfile:
            for result in results:
                outfile.write(' '.join(getattr(result[0], args.sequence_type))+'\n')
    else:
        print('No output file name provided.')
        print('Your search produced the results below:')
        for result in results:
            print('{}'.format(result[0]))
        print('Total number of results: {}'.format(str(len(results))))
        print('Please specify an output file name with -o to save these results.')


if __name__ == '__main__':
    main()