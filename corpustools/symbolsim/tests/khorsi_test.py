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

import corpustools.symbolsim.khorsi as khorsi

class KhorsiTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()
        self.relator = khorsi.Relator(self.corpus)

    def test_freq_base_spelling_type(self):
        expected = {'a':16,
                    'e':3,
                    'h':8,
                    'i':10,
                    'm':6,
                    'n':4,
                    'o':4,
                    's':13,
                    'ʃ':1,
                    't':11,
                    'u':4}
        freq_base = self.relator.make_freq_base('spelling','type')
        self.assertEqual(freq_base,expected)

    def test_freq_base_spelling_token(self):
        expected = {'a':466,
                    'e':118,
                    'h':538,
                    'i':429,
                    'm':156,
                    'n':142,
                    'o':171,
                    's':856,
                    'ʃ':2,
                    't':271,
                    'u':265}
        freq_base = self.relator.make_freq_base('spelling','token')
        self.assertEqual(freq_base,expected)

    def test_freq_base_transcription_type(self):
        expected = {'ɑ':16,
                    'e':3,
                    'i':10,
                    'm':6,
                    'n':4,
                    'o':4,
                    's':5,
                    'ʃ':9,
                    't':11,
                    'u':4}
        freq_base = self.relator.make_freq_base('transcription','type')
        self.assertEqual(freq_base,expected)

    def test_freq_base_transcription_token(self):
        expected = {'ɑ':466,
                    'e':118,
                    'i':429,
                    'm':156,
                    'n':142,
                    'o':171,
                    's':318,
                    'ʃ':540,
                    't':271,
                    'u':265}
        freq_base = self.relator.make_freq_base('transcription','token')
        self.assertEqual(freq_base,expected)

    def test_lcs_spelling(self):
        self.assertEqual(self.relator.lcs('atema','atema'),('atema',''))
        self.assertEqual(self.relator.lcs('atema','mashomisi'),('ma','shomisiate'))

    def test_lcs_transcription(self):
        self.assertEqual(self.relator.lcs(['ɑ','t','e','m','ɑ'],['ɑ','t','e','m','ɑ']),(['ɑ','t','e','m','ɑ'],[]))
        self.assertEqual(self.relator.lcs(['ɑ','t','e','m','ɑ'],['m','ɑ','ʃ','o','m','i','s','i']),(['m','ɑ'],['ʃ','o','m','i','s','i','ɑ','t','e']))


    def test_mass_relate_spelling_type(self):
        expected = [(11.0766887,self.corpus.find('atema')),
                    (-14.09489383,self.corpus.find('enuta')),
                    (-18.35890071,self.corpus.find('mashomisi')),
                    (-6.270847817,self.corpus.find('mata')),
                    (-8.494720336,self.corpus.find('nata')),
                    (-13.57140897,self.corpus.find('sasi')),
                    (-18.17657916,self.corpus.find('shashi')),
                    (-13.51516925,self.corpus.find('shisata')),
                    (-16.90806783,self.corpus.find('shushoma')),
                    (-8.717863887,self.corpus.find('ta')),
                    (-13.53912249,self.corpus.find('tatomi')),
                    (-28.78151269,self.corpus.find('tishenishu')),
                    (-15.17933206,self.corpus.find('toni')),
                    (-13.53067344,self.corpus.find('tusa')),
                    (-17.53815687,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[0])
        expected.reverse()
        calced = self.relator.mass_relate('atema',string_type='spelling',count_what = 'type')
        for i, v in enumerate(expected):
            print(v[1],calced[i][1])
            self.assertAlmostEqual(calced[i][0],v[0])

        expected = [(-13.57140897,self.corpus.find('atema')),
                    (-15.36316844,self.corpus.find('enuta')),
                    (-16.92481569,self.corpus.find('mashomisi')),
                    (-10.28799462,self.corpus.find('mata')),
                    (-10.69345973,self.corpus.find('nata')),
                    (7.323034009,self.corpus.find('sasi')),
                    (-8.971692634,self.corpus.find('shashi')),
                    (-10.26267682,self.corpus.find('shisata')),
                    (-20.30229654,self.corpus.find('shushoma')),
                    (-6.088289546,self.corpus.find('ta')),
                    (-15.73786189,self.corpus.find('tatomi')),
                    (-25.52902026,self.corpus.find('tishenishu')),
                    (-11.13974683,self.corpus.find('toni')),
                    (-5.449867265,self.corpus.find('tusa')),
                    (-7.54617756,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[0])
        expected.reverse()
        calced = self.relator.mass_relate('sasi',string_type='spelling',count_what = 'type')
        for i, v in enumerate(expected):
            self.assertAlmostEqual(calced[i][0],v[0])

    def test_mass_relate_spelling_token(self):
        expected = [(12.9671688,self.corpus.find('atema')),
                    (-16.49795651,self.corpus.find('enuta')),
                    (-17.65533907,self.corpus.find('mashomisi')),
                    (-7.337667817,self.corpus.find('mata')),
                    (-9.088485208,self.corpus.find('nata')),
                    (-13.8251823,self.corpus.find('sasi')),
                    (-17.52074498,self.corpus.find('shashi')),
                    (-12.59737574,self.corpus.find('shisata')),
                    (-14.82488063,self.corpus.find('shushoma')),
                    (-9.8915809,self.corpus.find('ta')),
                    (-14.6046824,self.corpus.find('tatomi')),
                    (-27.61147254,self.corpus.find('tishenishu')),
                    (-16.14809881,self.corpus.find('toni')),
                    (-13.8308605,self.corpus.find('tusa')),
                    (-22.4838445,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[0])
        expected.reverse()
        calced = self.relator.mass_relate('atema',string_type='spelling',count_what = 'token')
        for i, v in enumerate(expected):
            self.assertAlmostEqual(calced[i][0],v[0])

        expected = [(-13.8251823,self.corpus.find('atema')),
                    (-14.48366705,self.corpus.find('enuta')),
                    (-16.62778969,self.corpus.find('mashomisi')),
                    (-10.46022702,self.corpus.find('mata')),
                    (-10.55425597,self.corpus.find('nata')),
                    (6.832376308,self.corpus.find('sasi')),
                    (-7.235843913,self.corpus.find('shashi')),
                    (-9.913037922,self.corpus.find('shisata')),
                    (-19.77169406,self.corpus.find('shushoma')),
                    (-5.382988852,self.corpus.find('ta')),
                    (-16.07045316,self.corpus.find('tatomi')),
                    (-24.92713472,self.corpus.find('tishenishu')),
                    (-11.39132061,self.corpus.find('toni')),
                    (-5.172159875,self.corpus.find('tusa')),
                    (-10.12650306,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[0])
        expected.reverse()
        calced = self.relator.mass_relate('sasi',string_type='spelling',count_what = 'token')
        for i, v in enumerate(expected):
            self.assertAlmostEqual(calced[i][0],v[0])

    def test_mass_relate_transcription_type(self):
        expected = [(10.54988612,self.corpus.find('atema')),
                    (-13.35737022,self.corpus.find('enuta')),
                    (-16.64202823,self.corpus.find('mashomisi')),
                    (-5.95476627,self.corpus.find('mata')),
                    (-8.178638789,self.corpus.find('nata')),
                    (-14.85026877,self.corpus.find('sasi')),
                    (-13.67469544,self.corpus.find('shashi')),
                    (-12.0090178,self.corpus.find('shisata')),
                    (-12.51154463,self.corpus.find('shushoma')),
                    (-8.296421824,self.corpus.find('ta')),
                    (-13.01231991,self.corpus.find('tatomi')),
                    (-23.85818691,self.corpus.find('tishenishu')),
                    (-14.54716897,self.corpus.find('toni')),
                    (-13.85402179,self.corpus.find('tusa')),
                    (-14.60340869,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[0])
        expected.reverse()
        calced = self.relator.mass_relate('atema',string_type='transcription',count_what = 'type')
        for i, v in enumerate(expected):
            self.assertAlmostEqual(calced[i][0],v[0])

        expected = [(-14.85026877,self.corpus.find('atema')),
                    (-16.64202823,self.corpus.find('enuta')),
                    (-12.94778139,self.corpus.find('mashomisi')),
                    (-11.67221494,self.corpus.find('mata')),
                    (-12.07768004,self.corpus.find('nata')),
                    (8.812614836,self.corpus.find('sasi')),
                    (-11.93742415,self.corpus.find('shashi')),
                    (-7.90637444,self.corpus.find('shisata')),
                    (-18.22899329,self.corpus.find('shushoma')),
                    (-7.683230889,self.corpus.find('ta')),
                    (-16.91136117,self.corpus.find('tatomi')),
                    (-21.83498509,self.corpus.find('tishenishu')),
                    (-12.52396715,self.corpus.find('toni')),
                    (-5.239146233,self.corpus.find('tusa')),
                    (-6.943894326,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[0])
        expected.reverse()
        calced = self.relator.mass_relate('sasi',string_type='transcription',count_what = 'type')
        for i, v in enumerate(expected):
            self.assertAlmostEqual(calced[i][0],v[0])

    def test_mass_relate_transcription_token(self):
        expected = [(12.10974787,self.corpus.find('atema')),
                    (-15.29756722,self.corpus.find('enuta')),
                    (-16.05808867,self.corpus.find('mashomisi')),
                    (-8.574032654,self.corpus.find('mata')),
                    (-6.823215263,self.corpus.find('nata')),
                    (-14.77671518,self.corpus.find('sasi')),
                    (-13.71767966,self.corpus.find('shashi')),
                    (-11.34309371,self.corpus.find('shisata')),
                    (-11.19329949,self.corpus.find('shushoma')),
                    (-9.205644162,self.corpus.find('ta')),
                    (-13.74726148,self.corpus.find('tatomi')),
                    (-23.12247048,self.corpus.find('tishenishu')),
                    (-15.1191937,self.corpus.find('toni')),
                    (-13.79217439,self.corpus.find('tusa')),
                    (-15.68503325,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[0])
        expected.reverse()
        calced = self.relator.mass_relate('atema',string_type='transcription',count_what = 'token')
        for i, v in enumerate(expected):
            self.assertAlmostEqual(calced[i][0],v[0])

        expected = [(-14.77671518,self.corpus.find('atema')),
                    (-15.43519993,self.corpus.find('enuta')),
                    (-13.96361833,self.corpus.find('mashomisi')),
                    (-11.58324408,self.corpus.find('mata')),
                    (-11.67727303,self.corpus.find('nata')),
                    (8.126877557,self.corpus.find('sasi')),
                    (-9.734809346,self.corpus.find('shashi')),
                    (-7.840021077,self.corpus.find('shisata')),
                    (-15.95332831,self.corpus.find('shushoma')),
                    (-6.848974285,self.corpus.find('ta')),
                    (-16.85050186,self.corpus.find('tatomi')),
                    (-20.51761446,self.corpus.find('tishenishu')),
                    (-12.51433768,self.corpus.find('toni')),
                    (-4.829191506,self.corpus.find('tusa')),
                    (-5.994066536,self.corpus.find('ʃi')),]
        expected.sort(key=lambda t:t[0])
        expected.reverse()
        calced = self.relator.mass_relate('sasi',string_type='transcription',count_what = 'token')
        for i, v in enumerate(expected):
            self.assertAlmostEqual(calced[i][0],v[0])

if __name__ == '__main__':
    unittest.main()
