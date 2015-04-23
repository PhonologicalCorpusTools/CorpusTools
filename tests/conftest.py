#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import os
import sys

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix, Segment,
                                        Environment, EnvironmentFilter, Transcription,
                                        WordToken, Discourse)

from corpustools.utils import generate_discourse

from corpustools.gui.main import QApplicationMessaging
#@pytest.fixture(scope='session')
#def application():
#    from corpustools.gui.imports import QApplication
#    return QApplication([])


#Overwrite pytest-qt's qpp fixture
@pytest.yield_fixture(scope='session')
def qapp():
    """
    fixture that instantiates the QApplication instance that will be used by
    the tests.
    """
    app = QApplicationMessaging.instance()
    if app is None:
        app = QApplicationMessaging([])
        yield app
        app.exit()
    else:
        yield app # pragma: no cover

@pytest.fixture(scope='module')
def test_dir():
    test_dir = 'tests/data'
    if not os.path.exists(os.path.join(test_dir,'exported')):
        os.makedirs(os.path.join(test_dir,'exported'))
    return test_dir

@pytest.fixture(scope='session')
def settings():
    from corpustools.gui.config import Settings
    s = Settings()
    s['sigfigs'] = 3
    return Settings()

@pytest.fixture(scope='module')
def spe_specifier():
    corpus = specified_test_corpus()
    return corpus.specifier

@pytest.fixture(scope='module')
def unspecified_test_corpus():
    corpus_data = [{'spelling':'atema','transcription':['ɑ','t','e','m','ɑ'],'frequency':11.0},
                    {'spelling':'enuta','transcription':['e','n','u','t','ɑ'],'frequency':11.0},
                    {'spelling':'mashomisi','transcription':['m','ɑ','ʃ','o','m','i','s','i'],'frequency':5.0},
                    {'spelling':'mata','transcription':['m','ɑ','t','ɑ'],'frequency':2.0},
                    {'spelling':'nata','transcription':['n','ɑ','t','ɑ'],'frequency':2.0},
                    {'spelling':'sasi','transcription':['s','ɑ','s','i'],'frequency':139.0},
                    {'spelling':'shashi','transcription':['ʃ','ɑ','ʃ','i'],'frequency':43.0},
                    {'spelling':'shisata','transcription':['ʃ','i','s','ɑ','t','ɑ'],'frequency':3.0},
                    {'spelling':'shushoma','transcription':['ʃ','u','ʃ','o','m','ɑ'],'frequency':126.0},
                    {'spelling':'ta','transcription':['t','ɑ'],'frequency':67.0},
                    {'spelling':'tatomi','transcription':['t','ɑ','t','o','m','i'],'frequency':7.0},
                    {'spelling':'tishenishu','transcription':['t','i','ʃ','e','n','i','ʃ','u'],'frequency':96.0},
                    {'spelling':'toni','transcription':['t','o','n','i'],'frequency':33.0},
                    {'spelling':'tusa','transcription':['t','u','s','ɑ'],'frequency':32.0},
                    {'spelling':'ʃi','transcription':['ʃ','i'],'frequency':2.0}]
    corpus = Corpus('test')
    for w in corpus_data:
        corpus.add_word(Word(**w))
    return corpus

@pytest.fixture(scope='module')
def specified_test_corpus():
    fm = spe_specifier()
    corpus = unspecified_test_corpus()

    corpus.set_feature_matrix(fm)
    return corpus

@pytest.fixture(scope='module')
def unspecified_discourse_corpus():
    c = unspecified_test_corpus()
    d = generate_discourse(c)
    return d

@pytest.fixture(scope='module')
def spe_specifier():
    fm_input = [{'symbol':'ɑ','EXTRA':'-','LONG':'-','ant':'-','back':'+','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'n','low':'+','mv_glot_cl':'n','nasal':'-','round':'-','son':'+',
                'strid':'-','tense':'-','voc':'+','voice':'+'},
                {'symbol':'u','EXTRA':'-','LONG':'-','ant':'-','back':'+','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'+',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'-','round':'+','son':'+',
                'strid':'-','tense':'+','voc':'+','voice':'+'},
                {'symbol':'o','EXTRA':'-','LONG':'-','ant':'-','back':'+','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'-','round':'+','son':'+',
                'strid':'-','tense':'+','voc':'+','voice':'+'},
                {'symbol':'e','EXTRA':'-','LONG':'-','ant':'-','back':'-','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'+',
                'strid':'-','tense':'+','voc':'+','voice':'+'},
                {'symbol':'s','EXTRA':'-','LONG':'-','ant':'+','back':'-','cont':'+','cor':'+',
                'del_rel':'n','distr':'-','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'-','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'-',
                'strid':'+','tense':'.','voc':'-','voice':'-'},
                {'symbol':'m','EXTRA':'-','LONG':'-','ant':'+','back':'-','cont':'-','cor':'-',
                'del_rel':'-','distr':'+','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'+','round':'-','son':'+',
                'strid':'-','tense':'-','voc':'-','voice':'+'},
                {'symbol':'i','EXTRA':'-','LONG':'-','ant':'-','back':'-','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'+',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'+',
                'strid':'-','tense':'+','voc':'+','voice':'+'},
                {'symbol':'n','EXTRA':'-','LONG':'-','ant':'+','back':'-','cont':'-','cor':'+',
                'del_rel':'-','distr':'-','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'-','low':'-','mv_glot_cl':'n','nasal':'+','round':'-','son':'+',
                'strid':'-','tense':'-','voc':'-','voice':'+'},
                {'symbol':'ʃ','EXTRA':'-','LONG':'-','ant':'-','back':'-','cont':'+','cor':'+',
                'del_rel':'n','distr':'+','glot_cl':'-','hi_subgl_pr':'-','high':'+',
                'lat':'-','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'-',
                'strid':'+','tense':'.','voc':'-','voice':'-'},
                {'symbol':'t','EXTRA':'-','LONG':'-','ant':'+','back':'-','cont':'-','cor':'+',
                'del_rel':'-','distr':'-','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'-','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'-',
                'strid':'-','tense':'.','voc':'-','voice':'-'}]
    fm = FeatureMatrix('spe',fm_input)
    return fm

@pytest.fixture(scope='module')
def specified_discourse_corpus():
    fm = spe_specifier()
    c = unspecified_test_corpus()
    d = generate_discourse(c)
    d.lexicon.set_feature_matrix(fm)
    return d
