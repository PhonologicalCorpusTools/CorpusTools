import unittest

try:
    from corpustools.corpus.tests.classes_test import create_specified_test_corpus
except ImportError:
    import sys
    import os
    test_dir = os.path.dirname(os.path.abspath(__file__))
    corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(corpustools_path)
    from corpustools.corpus.tests.classes_test import create_specified_test_corpus

from corpustools.freqalt.freq_of_alt import calc_freq_of_alt

class FreqAltTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_specified_test_corpus()

    def test_freqalt(self):
        result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','type', min_rel = -15,
                                    phono_align=True)
        self.assertEqual(result,(8,3,0.375))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','token', min_rel = -15,
                                    phono_align=True)
        self.assertEqual(result,(8,3,0.375))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','type', min_rel = -6,
                                    phono_align=True)
        self.assertEqual(result,(8,0,0))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','token', min_rel = -6,
                                    phono_align=True)
        self.assertEqual(result,(8,2,0.25))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','type', min_rel = -15,
                                    phono_align=False)
        self.assertEqual(result,(8,7,0.875))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','token', min_rel = -15,
                                    phono_align=False)
        self.assertEqual(result,(8,7,0.875))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','type', min_rel = -6,
                                    phono_align=False)
        self.assertEqual(result,(8,2,0.25))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','token', min_rel = -6,
                                    phono_align=False)
        self.assertEqual(result,(8,3,0.375))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','edit_distance','type', max_rel = 2,
                                    phono_align=True)
        self.assertEqual(result,(8,3,0.375))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','edit_distance','token', max_rel = 4,
                                    phono_align=True)
        self.assertEqual(result,(8,3,0.375))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','edit_distance','type', max_rel = 2,
                                    phono_align=False, output_filename='nov4tests.txt')
        self.assertEqual(result,(8,2,0.25))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','edit_distance','token', max_rel = 4,
                                    phono_align=False)
        self.assertEqual(result,(8,3,0.375))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','phono_edit_distance','type', max_rel = 6,
                                    phono_align=True)
        self.assertEqual(result,(8,2,0.25))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','phono_edit_distance','token', max_rel = 20,
                                    phono_align=True)
        self.assertEqual(result,(8,3,0.375))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','phono_edit_distance','type', max_rel = 6,
                                    phono_align=False)
        self.assertEqual(result,(8,2,0.25))

        result = calc_freq_of_alt(self.corpus,'s','ʃ','phono_edit_distance','token', max_rel = 20,
                                    phono_align=False)
        self.assertEqual(result,(8,6,0.75))


if __name__ == '__main__':
    unittest.main()
