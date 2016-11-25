import argparse
from math import log
from collections import defaultdict
import os
import sys
from codecs import open

# default to importing from CorpusTools repo
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0,base)

from corpustools.corpus.classes import Corpus
from corpustools.corpus.io import load_binary
from corpustools.kl.kl import KullbackLeibler
from corpustools.contextmanagers import *

def main():

    #### Parse command-line arguments
    parser = argparse.ArgumentParser(description = 'Phonological CorpusTools: Kullback-Leibler CL interface')
    parser.add_argument('corpus_file_name', help='Path to corpus file. This can just be the file name if it\'s in the same directory as CorpusTools')
    parser.add_argument('seg1', help='First segment')
    parser.add_argument('seg2', help='Second segment')
    parser.add_argument('side', help='Context to check. Options are \'right\', \'left\' and \'both\'. You can enter just the first letter.')
    parser.add_argument('-s', '--sequence_type', default='transcription', help="The attribute of Words to calculate KL over. Normally this will be the transcription, but it can also be the spelling or a user-specified tier.")
    parser.add_argument('-t', '--type_or_token', default='token', help='Specifies whether entropy is based on type or token frequency.')
    parser.add_argument('-c', '--context_type', type=str, default='Canonical', help="How to deal with variable pronunciations. Options are 'Canonical', 'MostFrequent', 'SeparatedTokens', or 'Weighted'. See documentation for details.")
    parser.add_argument('-o', '--outfile', help='Name of output file (optional)')
    
    args = parser.parse_args()

    ####

    try:
        home = os.path.expanduser('~')
        corpus = load_binary(os.path.join(home, 'Documents', 'PCT', 'CorpusTools', 'CORPUS', args.corpus_file_name))
    except FileNotFoundError:
        corpus_path = args.corpus_file_name
        if not os.path.isfile(corpus_path):
            corpus_path = os.path.join(os.getcwd(), corpus_path)
        corpus = load_binary(corpus_path)

    if args.context_type == 'Canonical':
        corpus = CanonicalVariantContext(corpus, args.sequence_type, args.type_or_token)
    elif args.context_type == 'MostFrequent':
        corpus = MostFrequentVariantContext(corpus, args.sequence_type, args.type_or_token)
    elif args.context_type == 'SeparatedTokens':
        corpus = SeparatedTokensVariantContext(corpus, args.sequence_type, args.type_or_token)
    elif args.context_type == 'Weighted':
        corpus = WeightedVariantContext(corpus, args.sequence_type, args.type_or_token)

    results = KullbackLeibler(corpus, args.seg1, args.seg2, args.side, outfile=None)

    outfile = args.outfile
    if outfile is not None:
        if not os.path.isfile(outfile):
            outfile = os.path.join(os.getcwd(), outfile)
        if not outfile.endswith('.txt'):
            outfile += '.txt'

        with open(outfile, mode='w', encoding='utf-8-sig') as f:
            print('Seg1,Seg2,Seg1 entropy,Seg2 entropy,Possible UR, Spurious UR\n\r',file=f)
            print(','.join([str(r) for r in results]), file=f)
            print('\n\rContext,Context frequency,{} frequency in context,{} frequency in context\n\r'.format(seg1,seg2), file=f)
            for context,result in allC.items():
                cfrequency = freq_c[context]/totalC
                print('{},{},{},{}\n\r'.format(context,
                                cfrequency,
                                result.seg1/result.sum(),
                                result.seg2/result.sum()),
                        file=f)
        print('Done!')

    else:
        print(results)


if __name__ == '__main__':
    main()
