import unittest

try:
    from corpustools.corpus.tests.classes_test import create_unspecified_test_corpus
except ImportError:
    import sys
    import os
    test_dir = os.path.dirname(os.path.abspath(__file__))
    corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(corpustools_path)
    from corpustools.corpus.tests.classes_test import create_unspecified_test_corpus

from corpustools.symbolsim.string_similarity import mass_relate

class EditDistanceTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_spelling(self):
        expected = [(0,self.corpus.find('atema')),
                    (4,self.corpus.find('enuta')),
                    (7,self.corpus.find('mashomisi')),
                    (3,self.corpus.find('mata')),
                    (3,self.corpus.find('nata')),
                    (5,self.corpus.find('sasi')),
                    (6,self.corpus.find('shashi')),
                    (6,self.corpus.find('shisata')),
                    (6,self.corpus.find('shushoma')),
                    (3,self.corpus.find('ta')),
                    (3,self.corpus.find('tatomi')),
                    (9,self.corpus.find('tishenishu')),
                    (4,self.corpus.find('toni')),
                    (3,self.corpus.find('tusa')),
                    (5,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[1])
        calced = mass_relate(self.corpus,'atema','edit_distance',string_type='spelling')
        calced.sort(key=lambda t:t[1])
        for i, v in enumerate(expected):
            self.assertEqual(calced[i],v)


        expected = [(5,self.corpus.find('atema')),
                    (5,self.corpus.find('enuta')),
                    (6,self.corpus.find('mashomisi')),
                    (3,self.corpus.find('mata')),
                    (3,self.corpus.find('nata')),
                    (0,self.corpus.find('sasi')),
                    (2,self.corpus.find('shashi')),
                    (5,self.corpus.find('shisata')),
                    (6,self.corpus.find('shushoma')),
                    (3,self.corpus.find('ta')),
                    (4,self.corpus.find('tatomi')),
                    (8,self.corpus.find('tishenishu')),
                    (3,self.corpus.find('toni')),
                    (3,self.corpus.find('tusa')),
                    (3,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[1])
        calced = mass_relate(self.corpus,'sasi','edit_distance',string_type='spelling')
        calced.sort(key=lambda t:t[1])
        for i, v in enumerate(expected):
            self.assertEqual(calced[i],v)

    def test_transcription(self):
        expected = [(0,self.corpus.find('atema')),
                    (4,self.corpus.find('enuta')),
                    (6,self.corpus.find('mashomisi')),
                    (3,self.corpus.find('mata')),
                    (3,self.corpus.find('nata')),
                    (5,self.corpus.find('sasi')),
                    (5,self.corpus.find('shashi')),
                    (5,self.corpus.find('shisata')),
                    (4,self.corpus.find('shushoma')),
                    (3,self.corpus.find('ta')),
                    (3,self.corpus.find('tatomi')),
                    (7,self.corpus.find('tishenishu')),
                    (4,self.corpus.find('toni')),
                    (3,self.corpus.find('tusa')),
                    (5,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[1])
        calced = mass_relate(self.corpus,'atema','edit_distance',string_type='transcription')
        calced.sort(key=lambda t:t[1])
        for i, v in enumerate(expected):
            self.assertEqual(calced[i],v)


        expected = [(5,self.corpus.find('atema')),
                    (5,self.corpus.find('enuta')),
                    (5,self.corpus.find('mashomisi')),
                    (3,self.corpus.find('mata')),
                    (3,self.corpus.find('nata')),
                    (0,self.corpus.find('sasi')),
                    (2,self.corpus.find('shashi')),
                    (4,self.corpus.find('shisata')),
                    (6,self.corpus.find('shushoma')),
                    (3,self.corpus.find('ta')),
                    (4,self.corpus.find('tatomi')),
                    (7,self.corpus.find('tishenishu')),
                    (3,self.corpus.find('toni')),
                    (3,self.corpus.find('tusa')),
                    (3,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[1])
        calced = mass_relate(self.corpus,'sasi','edit_distance',string_type='transcription')
        calced.sort(key=lambda t:t[1])
        for i, v in enumerate(expected):
            self.assertEqual(calced[i][0],v[0])

if __name__ == '__main__':
    unittest.main()
