import unittest

import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
print(corpustools_path)
sys.path.insert(0, corpustools_path)
from corpustools.corpus.tests.classes_test import create_unspecified_test_corpus

from corpustools.symbolsim.string_similarity import string_similarity

class EditDistanceTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_spelling(self):
        expected = [(self.corpus.find('atema'),self.corpus.find('atema'),0),
                    (self.corpus.find('atema'),self.corpus.find('enuta'),4),
                    (self.corpus.find('atema'),self.corpus.find('mashomisi'),7),
                    (self.corpus.find('atema'),self.corpus.find('mata'),3),
                    (self.corpus.find('atema'),self.corpus.find('nata'),3),
                    (self.corpus.find('atema'),self.corpus.find('sasi'),5),
                    (self.corpus.find('atema'),self.corpus.find('shashi'),6),
                    (self.corpus.find('atema'),self.corpus.find('shisata'),6),
                    (self.corpus.find('atema'),self.corpus.find('shushoma'),6),
                    (self.corpus.find('atema'),self.corpus.find('ta'),3),
                    (self.corpus.find('atema'),self.corpus.find('tatomi'),3),
                    (self.corpus.find('atema'),self.corpus.find('tishenishu'),9),
                    (self.corpus.find('atema'),self.corpus.find('toni'),4),
                    (self.corpus.find('atema'),self.corpus.find('tusa'),3),
                    (self.corpus.find('atema'),self.corpus.find('ʃi'),5)]
        expected.sort(key=lambda t:t[1])
        calced = string_similarity(self.corpus,'atema','edit_distance',string_type='spelling')
        calced.sort(key=lambda t:t[1])
        for i, v in enumerate(expected):
            self.assertEqual(calced[i],v)

        expected = [(self.corpus.find('sasi'),self.corpus.find('atema'),5),
                    (self.corpus.find('sasi'),self.corpus.find('enuta'),5),
                    (self.corpus.find('sasi'),self.corpus.find('mashomisi'),6),
                    (self.corpus.find('sasi'),self.corpus.find('mata'),3),
                    (self.corpus.find('sasi'),self.corpus.find('nata'),3),
                    (self.corpus.find('sasi'),self.corpus.find('sasi'),0),
                    (self.corpus.find('sasi'),self.corpus.find('shashi'),2),
                    (self.corpus.find('sasi'),self.corpus.find('shisata'),5),
                    (self.corpus.find('sasi'),self.corpus.find('shushoma'),6),
                    (self.corpus.find('sasi'),self.corpus.find('ta'),3),
                    (self.corpus.find('sasi'),self.corpus.find('tatomi'),4),
                    (self.corpus.find('sasi'),self.corpus.find('tishenishu'),8),
                    (self.corpus.find('sasi'),self.corpus.find('toni'),3),
                    (self.corpus.find('sasi'),self.corpus.find('tusa'),3),
                    (self.corpus.find('sasi'),self.corpus.find('ʃi'),3)]
        expected.sort(key=lambda t:t[1])
        calced = string_similarity(self.corpus,'sasi','edit_distance',string_type='spelling')
        calced.sort(key=lambda t:t[1])
        for i, v in enumerate(expected):
            self.assertEqual(calced[i],v)

    def test_transcription(self):
        expected = [(self.corpus.find('atema'),self.corpus.find('atema'),0),
                    (self.corpus.find('atema'),self.corpus.find('enuta'),4),
                    (self.corpus.find('atema'),self.corpus.find('mashomisi'),6),
                    (self.corpus.find('atema'),self.corpus.find('mata'),3),
                    (self.corpus.find('atema'),self.corpus.find('nata'),3),
                    (self.corpus.find('atema'),self.corpus.find('sasi'),5),
                    (self.corpus.find('atema'),self.corpus.find('shashi'),5),
                    (self.corpus.find('atema'),self.corpus.find('shisata'),5),
                    (self.corpus.find('atema'),self.corpus.find('shushoma'),4),
                    (self.corpus.find('atema'),self.corpus.find('ta'),3),
                    (self.corpus.find('atema'),self.corpus.find('tatomi'),3),
                    (self.corpus.find('atema'),self.corpus.find('tishenishu'),7),
                    (self.corpus.find('atema'),self.corpus.find('toni'),4),
                    (self.corpus.find('atema'),self.corpus.find('tusa'),3),
                    (self.corpus.find('atema'),self.corpus.find('ʃi'),5)]
        expected.sort(key=lambda t:t[1])
        calced = string_similarity(self.corpus,'atema','edit_distance',string_type='transcription')
        calced.sort(key=lambda t:t[1])
        for i, v in enumerate(expected):
            self.assertEqual(calced[i],v)

        expected = [(self.corpus.find('sasi'),self.corpus.find('atema'),5),
                    (self.corpus.find('sasi'),self.corpus.find('enuta'),5),
                    (self.corpus.find('sasi'),self.corpus.find('mashomisi'),5),
                    (self.corpus.find('sasi'),self.corpus.find('mata'),3),
                    (self.corpus.find('sasi'),self.corpus.find('nata'),3),
                    (self.corpus.find('sasi'),self.corpus.find('sasi'),0),
                    (self.corpus.find('sasi'),self.corpus.find('shashi'),2),
                    (self.corpus.find('sasi'),self.corpus.find('shisata'),4),
                    (self.corpus.find('sasi'),self.corpus.find('shushoma'),6),
                    (self.corpus.find('sasi'),self.corpus.find('ta'),3),
                    (self.corpus.find('sasi'),self.corpus.find('tatomi'),4),
                    (self.corpus.find('sasi'),self.corpus.find('tishenishu'),7),
                    (self.corpus.find('sasi'),self.corpus.find('toni'),3),
                    (self.corpus.find('sasi'),self.corpus.find('tusa'),3),
                    (self.corpus.find('sasi'),self.corpus.find('ʃi'),3)]
        expected.sort(key=lambda t:t[1])
        calced = string_similarity(self.corpus,'sasi','edit_distance',string_type='transcription')
        calced.sort(key=lambda t:t[1])
        for i, v in enumerate(expected):
            self.assertEqual(calced[i],v)

if __name__ == '__main__':
    unittest.main()
