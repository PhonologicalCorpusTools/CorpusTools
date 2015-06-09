
import pytest
import os
import sys

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix,
                                        Environment, EnvironmentFilter, Transcription,
                                        WordToken, Discourse, SpontaneousSpeechCorpus)


def test_init():
    word_type_only = {'begin':0,'end':1,'word':Word(**{'spelling':'a','transcription':['a','b']})}

    word_type_and = {'begin':0,'end':1,'spelling':'a2','transcription':['a','b2'],
                        'word':Word(**{'spelling':'a','transcription':['a','b']})}
    wt = WordToken(**word_type_only)
    assert(wt.spelling == 'a')
    assert(str(wt.transcription) == 'a.b')

    wt = WordToken(**word_type_and)
    assert(wt.spelling == 'a2')
    assert(str(wt.transcription) == 'a.b2')

def test_duration():
    word_tokens = [{'begin':0,'end':1,'spelling':'a','transcription':['a','b']},
                    {'begin':1,'end':2,'spelling':'c','transcription':['c','a','b']},
                    {'begin':2,'end':3,'spelling':'a','transcription':['a','b']},
                    {'begin':3,'end':4,'spelling':'d','transcription':['a','d']}]
    for wt in word_tokens:
        w = WordToken(**wt)
        assert(w.duration == 1)

def test_init():
    word_tokens = [{'begin':0,'end':1,'word':Word(**{'spelling':'a','transcription':['a','b']})},
                    {'begin':1,'end':2,'word':Word(**{'spelling':'c','transcription':['c','a','b']})},
                    {'begin':2,'end':3,'word':Word(**{'spelling':'a','transcription':['a','b']})},
                    {'begin':3,'end':4,'word':Word(**{'spelling':'d','transcription':['a','d']})}]
    d = Discourse()
    for wt in word_tokens:
        d.add_word(WordToken(**wt))

    #assert(d[0].previous_token, None)
    #assert(d[1].previous_token, d[0])

def test_init():
    word_tokens = [{'begin':0,'end':1,'word':{'spelling':'a','transcription':['a','b']},'following_token_time':1},
                    {'begin':1,'end':2,'word':{'spelling':'c','transcription':['c','a','b']}, 'previous_token_time':0,'following_token_time':2},
                    {'begin':2,'end':3,'word':{'spelling':'a','transcription':['a','b']}, 'previous_token_time':1,'following_token_time':3},
                    {'begin':3,'end':4,'word':{'spelling':'d','transcription':['a','d']}, 'previous_token_time':2,}]
    d = Discourse()
    for wt in word_tokens:
        w = d.lexicon.get_or_create_word(**wt['word'])
        w.frequency += 1
        wt['word'] = w
        d.add_word(WordToken(**wt))
    corpus = SpontaneousSpeechCorpus('','')

    corpus.add_discourse(d)

    d = corpus.discourses['']

    assert(d[0].wordtype.frequency == 2)
    assert(d[1].wordtype.frequency == 1)
