
import pytest
import os

from corpustools.corpus.io.multiple_files import (read_phones, read_words,
                            BaseAnnotation,
                            multiple_files_to_data)

def test_load_phones(buckeye_test_dir):
    expected_phones = [BaseAnnotation('{B_TRANS}',0.0, 2.609000),
                            BaseAnnotation('IVER',2.609000, 2.714347),
                            BaseAnnotation('eh',2.714347, 2.753000),
                            BaseAnnotation('s',2.753000, 2.892000),
                            BaseAnnotation('IVER',2.892000, 3.206890),
                            BaseAnnotation('dh',3.206890, 3.244160),
                            BaseAnnotation('ae',3.244160, 3.327000),
                            BaseAnnotation('s',3.327000, 3.377192),
                            BaseAnnotation('s',3.377192, 3.438544),
                            BaseAnnotation('ae',3.438544, 3.526272),
                            BaseAnnotation('tq',3.526272, 3.614398),
                            BaseAnnotation('VOCNOISE',3.614398, 3.673454),
                            BaseAnnotation('ah',3.673454, 3.718614),
                            BaseAnnotation('w',3.718614, 3.771112),
                            BaseAnnotation('ah',3.771112, 3.851000),
                            BaseAnnotation('dx',3.851000, 3.881000),
                            BaseAnnotation('eh',3.881000, 3.941000),
                            BaseAnnotation('v',3.941000, 4.001000),
                            BaseAnnotation('er',4.001000, 4.036022),
                            BaseAnnotation('ey',4.036022, 4.111000),
                            BaseAnnotation('k',4.111000, 4.246000),
                            BaseAnnotation('ao',4.246000, 4.326000),
                            BaseAnnotation('l',4.326000, 4.369000),
                            BaseAnnotation('ah',4.369000, 4.443707),
                            BaseAnnotation('t',4.443707, 4.501000),
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


