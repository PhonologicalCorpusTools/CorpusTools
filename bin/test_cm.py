import os
import sys
base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0,base)
from corpustools.gui.main import MainWindow,QApplicationMessaging
from corpustools.symbolsim.string_similarity import string_similarity as ss
from corpustools.contextmanagers import *
 
#corpus_name = 'example'
corpus_name = 'Speakers'
corpus = lb('C:\\Users\\Michael\\Documents\\PCT\\CorpusTools\\CORPUS\\' + corpus_name + '.corpus')
outf_name = 'C:\\Users\\Michael\\Desktop\\' + corpus_name + '_test_out.txt'

with MostFrequentVariantContext(getattr(corpus, 'lexicon'), 'transcription', 'type') as c:
    counter = 0
    for word in c:
        counter += 1
    print(counter)
