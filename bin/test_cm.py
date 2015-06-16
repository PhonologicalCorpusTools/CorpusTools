import os
import sys
base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0,base)

from corpustools.corpus.classes.lexicon import Word
from corpustools.corpus.io.binary import load_binary as lb
from corpustools.symbolsim.string_similarity import string_similarity as ss
from corpustools.contextmanagers import *

corpus_name = 'Speakers'
corpus = lb('C:\\Users\\Michael\\Documents\\PCT\\CorpusTools\\CORPUS\\' + corpus_name + '.corpus')
outf_name = 'C:\\Users\\Michael\\Desktop\\' + corpus_name + '_test_out.txt'

if corpus_name == 'Speakers':
    corpus = getattr(corpus, 'lexicon')

with CanonicalVariantContext(corpus, 'transcription', 'type') as c:
    counter = 0
    freq = 0
    for word in c:
        counter += 1
        freq += word.frequency
        #if word.spelling == 'nata':
            #w1 = word
        #if word.spelling == 'mata':
            #w2 = word
    print(counter)
    print(freq)
            
    #a = ss(c, (w1, w2), 'khorsi')
    #print(a)


with MostFrequentVariantContext(corpus, 'transcription', 'type') as c:
    counter = 0
    freq = 0
    for word in c:
        counter += 1
        freq += word.frequency
    print(counter)
    print(freq)

with SeparatedTokensVariantContext(corpus, 'transcription', 'type') as c:
    counter = 0
    freq = 0
    for word in c:
        counter += 1
        freq += word.frequency
    print(counter)
    print(freq)

with WeightedVariantContext(corpus, 'transcription', 'type') as c:
    counter = 0
    freq = 0
    for word in c:
        counter += 1
        freq += word.frequency
    print(counter)
    print(freq)


with CanonicalVariantContext(corpus, 'transcription', 'token') as c:
    counter = 0
    freq = 0
    for word in c:
        counter += 1
        freq += word.frequency
        #if word.spelling == 'nata':
            #w1 = word
        #if word.spelling == 'mata':
            #w2 = word
    print(counter)
    print(freq)
            
    #a = ss(c, (w1, w2), 'khorsi')
    #print(a)


with MostFrequentVariantContext(corpus, 'transcription', 'token') as c:
    counter = 0
    freq = 0
    for word in c:
        counter += 1
        freq += word.frequency
    print(counter)
    print(freq)

with SeparatedTokensVariantContext(corpus, 'transcription', 'token') as c:
    counter = 0
    freq = 0
    for word in c:
        counter += 1
        freq += word.frequency
    print(counter)
    print(freq)

with WeightedVariantContext(corpus, 'transcription', 'token') as c:
    counter = 0
    freq = 0
    for word in c:
        counter += 1
        freq += word.frequency
    print(counter)
    print(freq)
