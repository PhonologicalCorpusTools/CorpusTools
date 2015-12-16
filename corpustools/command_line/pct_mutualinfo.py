import argparse
import os
import sys
import csv

# default to importing from CorpusTools repo
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0,base)

from corpustools.corpus.io import load_binary
from corpustools.mutualinfo.mutual_information import *
from corpustools.contextmanagers import *


def main():

    #### Parse command-line arguments
    parser = argparse.ArgumentParser(description = \
             'Phonological CorpusTools: mutual information CL interface')
    parser.add_argument('corpus_file_name', help='Name of corpus file')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-q', '--query', help='bigram or segment pair, as str separated by comma')
    group.add_argument('-l', '--all_pairwise_mis', action='store_true', help="Calculate MI for all orders of all pairs of segments")
    parser.add_argument('-c', '--context_type', type=str, default='Canonical', help="How to deal with variable pronunciations. Options are 'Canonical', 'MostFrequent', 'SeparatedTokens', or 'Weighted'. See documentation for details.")
    parser.add_argument('-s', '--sequence_type', default='transcription', help="The attribute of Words to calculate MI over. Normally this will be the transcription, but it can also be the spelling or a user-specified tier.")
    parser.add_argument('-w', '--in_word', action='store_true', help="Flag: domain for counting unigrams/bigrams set to the word rather than the unigram/bigram; ignores adjacency and word edges (#)")
    parser.add_argument('-e', '--halve_edges', action='store_true', help="Flag: make the number of edge characters (#) equal to the size of the corpus + 1, rather than double the size of the corpus - 1")
    parser.add_argument('-o', '--outfile', help='Name of output file')

    args = parser.parse_args()

    ####

    try:
        home = os.path.expanduser('~')
        corpus = load_binary(os.path.join(home, 'Documents', 'PCT', 'CorpusTools', 'CORPUS', args.corpus_file_name))
    except FileNotFoundError:
        corpus = load_binary(args.corpus_file_name)

    if args.context_type == 'Canonical':
        corpus = CanonicalVariantContext(corpus, args.sequence_type)
    elif args.context_type == 'MostFrequent':
        corpus = MostFrequentVariantContext(corpus, args.sequence_type)
    elif args.context_type == 'SeparatedTokens':
        corpus = SeparatedTokensVariantContext(corpus, args.sequence_type)
    elif args.context_type == 'Weighted':
        corpus = WeightedVariantContext(corpus, args.sequence_type)


    if args.all_pairwise_mis:
        result = all_mis(corpus, halve_edges = args.halve_edges, in_word = args.in_word)

    else:
        query = tuple(args.query.split(','))
        if len(query) < 2:
            print('Warning! Your queried bigram could not be processed. Please separate the two segments with a comma, as in the call: pct_mutualinfo example.corpus m,a')

        result = pointwise_mi(corpus, query, args.halve_edges, args.in_word)

    if args.outfile:
        with open(args.outfile, 'w') as outfile:
            if type(result) != list:
                outstr = 'result\t' + '\t'.join([a for a in vars(args)]) + '\n' + str(result) + '\t' + '\t'.join([str(getattr(args, a)) for a in vars(args)])
                outfile.write(outstr)
            else:
                outstr = 'result\tsegments\t' + '\t'.join([a for a in vars(args)]) + '\n'
                for element in result:
                    outstr += str(element[1]) + '\t' + str(element[0]) + '\t' + '\t'.join([str(getattr(args,a)) for a in vars(args)]) + '\n'
                outfile.write(outstr)
    else:
        print('No output file name provided.')
        print('The mutual information of the given inputs is {}.'.format(str(result)))


if __name__ == '__main__':
    main()
