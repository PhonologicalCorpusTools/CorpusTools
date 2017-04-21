import corpustools.corpus.io.csv as csv
import os

name = 'LF'
path = os.path.join(os.getcwd(), 'LF_closed_monosyllables.txt')
delim = '\t'

corpus = csv.load_corpus_csv(name, path, delim)
