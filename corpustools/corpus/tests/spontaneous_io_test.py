
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,corpustools_path)

from corpustools.corpus.io.spontaneous import (load_phones, load_words,
                            files_to_data, import_spontaneous_speech_corpus)

buckeye_path = r'C:\Users\michael\Dropbox\Measuring_Phonological_Relations\Computational\CorpusTools_test_files\Corpus_loading\spontaneous\buckeye'

class PhoneFileLoadTest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(buckeye_path, 's0201a.phones')
        self.expected_phones = [{'label':'{B_TRANS}','begin':0.0,'end':2.609000},
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

    def test_load_phones(self):
        phones = load_phones(self.path)
        for i,p in enumerate(self.expected_phones):
            self.assertEqual(p,phones[i])

class WordFileLoadTest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(buckeye_path, 's0201a.words')
        self.expected_words = [{'word':'{B_TRANS}','begin':0,'end':2.609000,'ur':None,'sr':None,'category':None},
            {'word':'<IVER>','begin':2.609000,'end':2.714347,'ur':None,'sr':None,'category':None},
            {'word':'that\'s','begin':2.714347,'end':2.892096,'ur':['dh', 'ae', 't', 's'],'sr':['eh', 's'],'category':'DT_VBZ'},
            {'word':'<IVER>','begin':2.892096,'end':3.206317,'ur':None,'sr':None,'category':None},
            {'word':'that\'s','begin':3.206317,'end':3.377192,'ur':['dh', 'ae', 't', 's'],'sr':['dh','ae','s'],'category':'DT_VBZ'},
            {'word':'that','begin':3.377192,'end':3.614398,'ur':['dh','ae','t'],'sr':['s','ae','tq'],'category':'IN'},
            {'word':'<VOCNOISE>','begin':3.614398,'end':3.673454,'ur':None,'sr':None,'category':None},
            {'word':'whatever','begin':3.673454,'end':4.036022,'ur':['w','ah','t','eh','v','er'],'sr':['ah','w','ah','dx','eh','v','er'],'category':'WDT'},
            {'word':'they','begin':4.036022,'end':4.111000,'ur':['dh','ey'],'sr':['ey'],'category':'PRP'},
            {'word':'call','begin':4.111000,'end':4.369000,'ur':['k','aa','l'],'sr':['k','ao','l'],'category':'VBP'},
            {'word':'it','begin':4.369000,'end':4.501000,'ur':['ih','t'],'sr':['ah','t'],'category':'PRP'}]

    def test_load_words(self):
        words = load_words(self.path)
        for i,w in enumerate(self.expected_words):
            self.assertEqual(w,words[i])

class WordPhoneLoadTest(unittest.TestCase):
    def test_files_to_data(self):
        pass
        #words = files_to_data(buckeye_path,'s0201a')

class ImportTest(unittest.TestCase):
    def test_import(self):
        corpus = import_spontaneous_speech_corpus('Buckeye',buckeye_path)

if __name__ == '__main__':

    unittest.main()
