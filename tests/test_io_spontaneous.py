
import pytest
import os

from corpustools.corpus.io.spontaneous import import_spontaneous_speech_corpus

def test_import_buckeye(buckeye_test_dir):
    corpus = import_spontaneous_speech_corpus('',buckeye_test_dir,dialect = 'buckeye')
    #print(list(corpus.discourses.keys()))

def test_import_textgrids(textgrid_test_dir):
    pass
    #corpus = import_spontaneous_speech_corpus('',textgrid_test_dir, dialect = 'textgrid')
    #print(list(corpus.discourses.keys()))

