
import pytest
import os

from corpustools.corpus.io.multiple_files import (read_phones, read_words,
                            multiple_files_to_data)

def test_load_phones(buckeye_test_dir):
    expected_phones = [{'symbol':'{B_TRANS}','begin':0.0,'end':2.609000},
                            {'symbol':'IVER','begin':2.609000,'end':2.714347},
                            {'symbol':'eh','begin':2.714347,'end':2.753000},
                            {'symbol':'s','begin':2.753000,'end':2.892000},
                            {'symbol':'IVER','begin':2.892000,'end':3.206890},
                            {'symbol':'dh','begin':3.206890,'end':3.244160},
                            {'symbol':'ae','begin':3.244160,'end':3.327000},
                            {'symbol':'s','begin':3.327000,'end':3.377192},
                            {'symbol':'s','begin':3.377192,'end':3.438544},
                            {'symbol':'ae','begin':3.438544,'end':3.526272},
                            {'symbol':'tq','begin':3.526272,'end':3.614398},
                            {'symbol':'VOCNOISE','begin':3.614398,'end':3.673454},
                            {'symbol':'ah','begin':3.673454,'end':3.718614},
                            {'symbol':'w','begin':3.718614,'end':3.771112},
                            {'symbol':'ah','begin':3.771112,'end':3.851000},
                            {'symbol':'dx','begin':3.851000,'end':3.881000},
                            {'symbol':'eh','begin':3.881000,'end':3.941000},
                            {'symbol':'v','begin':3.941000,'end':4.001000},
                            {'symbol':'er','begin':4.001000,'end':4.036022},
                            {'symbol':'ey','begin':4.036022,'end':4.111000},
                            {'symbol':'k','begin':4.111000,'end':4.246000},
                            {'symbol':'ao','begin':4.246000,'end':4.326000},
                            {'symbol':'l','begin':4.326000,'end':4.369000},
                            {'symbol':'ah','begin':4.369000,'end':4.443707},
                            {'symbol':'t','begin':4.443707,'end':4.501000},
                            ]
    phones = read_phones(os.path.join(buckeye_test_dir,'test.phones'),dialect='buckeye')
    for i,p in enumerate(expected_phones):
        assert(p == phones[i])

def test_load_words(buckeye_test_dir):
    words = read_words(os.path.join(buckeye_test_dir, 'test.words'),dialect='buckeye')
    expected_words = [{'lookup_spelling':'{B_TRANS}','Begin':0,'End':2.609000,'lookup_transcription':None,'sr':None,'Category':None},
        {'lookup_spelling':'<IVER>','Begin':2.609000,'End':2.714347,'lookup_transcription':None,'sr':None,'Category':None},
        {'lookup_spelling':'that\'s','Begin':2.714347,'End':2.892096,'lookup_transcription':['dh', 'ae', 't', 's'],'sr':['eh', 's'],'Category':'DT_VBZ'},
        {'lookup_spelling':'<IVER>','Begin':2.892096,'End':3.206317,'lookup_transcription':None,'sr':None,'Category':None},
        {'lookup_spelling':'that\'s','Begin':3.206317,'End':3.377192,'lookup_transcription':['dh', 'ae', 't', 's'],'sr':['dh','ae','s'],'Category':'DT_VBZ'},
        {'lookup_spelling':'that','Begin':3.377192,'End':3.614398,'lookup_transcription':['dh','ae','t'],'sr':['s','ae','tq'],'Category':'IN'},
        {'lookup_spelling':'<VOCNOISE>','Begin':3.614398,'End':3.673454,'lookup_transcription':None,'sr':None,'Category':None},
        {'lookup_spelling':'whatever','Begin':3.673454,'End':4.036022,'lookup_transcription':['w','ah','t','eh','v','er'],'sr':['ah','w','ah','dx','eh','v','er'],'Category':'WDT'},
        {'lookup_spelling':'they','Begin':4.036022,'End':4.111000,'lookup_transcription':['dh','ey'],'sr':['ey'],'Category':'PRP'},
        {'lookup_spelling':'call','Begin':4.111000,'End':4.369000,'lookup_transcription':['k','aa','l'],'sr':['k','ao','l'],'Category':'VBP'},
        {'lookup_spelling':'it','Begin':4.369000,'End':4.501000,'lookup_transcription':['ih','t'],'sr':['ah','t'],'Category':'PRP'}]
    for i,w in enumerate(expected_words):
        assert(w == words[i])

def test_files_to_data(buckeye_test_dir):
    words = multiple_files_to_data(os.path.join(buckeye_test_dir,'test.words'),os.path.join(buckeye_test_dir,'test.phones'), 'buckeye')


