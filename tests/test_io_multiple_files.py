
import pytest
import os

from corpustools.corpus.io.multiple_files import (read_phones, read_words,
                            multiple_files_to_data)

def test_load_phones(buckeye_test_dir):
    expected_phones = [{'label':'{B_TRANS}','begin':0.0,'end':2.609000},
                            {'label':'IVER','begin':2.609000,'end':2.714347},
                            {'label':'eh','begin':2.714347,'end':2.753000},
                            {'label':'s','begin':2.753000,'end':2.892000},
                            {'label':'IVER','begin':2.892000,'end':3.206890},
                            {'label':'dh','begin':3.206890,'end':3.244160},
                            {'label':'ae','begin':3.244160,'end':3.327000},
                            {'label':'s','begin':3.327000,'end':3.377192},
                            {'label':'s','begin':3.377192,'end':3.438544},
                            {'label':'ae','begin':3.438544,'end':3.526272},
                            {'label':'tq','begin':3.526272,'end':3.614398},
                            {'label':'VOCNOISE','begin':3.614398,'end':3.673454},
                            {'label':'ah','begin':3.673454,'end':3.718614},
                            {'label':'w','begin':3.718614,'end':3.771112},
                            {'label':'ah','begin':3.771112,'end':3.851000},
                            {'label':'dx','begin':3.851000,'end':3.881000},
                            {'label':'eh','begin':3.881000,'end':3.941000},
                            {'label':'v','begin':3.941000,'end':4.001000},
                            {'label':'er','begin':4.001000,'end':4.036022},
                            {'label':'ey','begin':4.036022,'end':4.111000},
                            {'label':'k','begin':4.111000,'end':4.246000},
                            {'label':'ao','begin':4.246000,'end':4.326000},
                            {'label':'l','begin':4.326000,'end':4.369000},
                            {'label':'ah','begin':4.369000,'end':4.443707},
                            {'label':'t','begin':4.443707,'end':4.501000},
                            ]
    phones = read_phones(os.path.join(buckeye_test_dir,'test.phones'),dialect='buckeye')
    for i,p in enumerate(expected_phones):
        assert(p == phones[i])

def test_load_words(buckeye_test_dir):
    words = read_words(os.path.join(buckeye_test_dir, 'test.words'),dialect='buckeye')
    expected_words = [{'spelling':'{B_TRANS}','begin':0,'end':2.609000,'transcription':None,'surface_transcription':None,'category':None},
        {'spelling':'<IVER>','begin':2.609000,'end':2.714347,'transcription':None,'surface_transcription':None,'category':None},
        {'spelling':'that\'s','begin':2.714347,'end':2.892096,'transcription':['dh', 'ae', 't', 's'],'surface_transcription':['eh', 's'],'category':'DT_VBZ'},
        {'spelling':'<IVER>','begin':2.892096,'end':3.206317,'transcription':None,'surface_transcription':None,'category':None},
        {'spelling':'that\'s','begin':3.206317,'end':3.377192,'transcription':['dh', 'ae', 't', 's'],'surface_transcription':['dh','ae','s'],'category':'DT_VBZ'},
        {'spelling':'that','begin':3.377192,'end':3.614398,'transcription':['dh','ae','t'],'surface_transcription':['s','ae','tq'],'category':'IN'},
        {'spelling':'<VOCNOISE>','begin':3.614398,'end':3.673454,'transcription':None,'surface_transcription':None,'category':None},
        {'spelling':'whatever','begin':3.673454,'end':4.036022,'transcription':['w','ah','t','eh','v','er'],'surface_transcription':['ah','w','ah','dx','eh','v','er'],'category':'WDT'},
        {'spelling':'they','begin':4.036022,'end':4.111000,'transcription':['dh','ey'],'surface_transcription':['ey'],'category':'PRP'},
        {'spelling':'call','begin':4.111000,'end':4.369000,'transcription':['k','aa','l'],'surface_transcription':['k','ao','l'],'category':'VBP'},
        {'spelling':'it','begin':4.369000,'end':4.501000,'transcription':['ih','t'],'surface_transcription':['ah','t'],'category':'PRP'}]
    for i,w in enumerate(expected_words):
        assert(w == words[i])

def test_files_to_data(buckeye_test_dir):
    words = multiple_files_to_data(os.path.join(buckeye_test_dir,'test.words'),os.path.join(buckeye_test_dir,'test.phones'), 'buckeye')


