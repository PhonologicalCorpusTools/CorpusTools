import unittest

import os
try:
    from phonsim.helpers.distance_functions import (dtw_distance,
                                        generate_distance_matrix,
                                        xcorr_distance)
except ImportError:
    import sys
    test_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.split(os.path.split(test_dir)[0])[0])
    from phonsim.phon_sim import phonetic_similarity_mapping,phonetic_similarity_directories

TEST_DIR = r'C:\Users\michael\Documents\Testing'

class RuntimeTest(unittest.TestCase):
    def setUp(self):
        self.dir_one_path = os.path.join(TEST_DIR,'dir_one')
        self.dir_two_path = os.path.join(TEST_DIR,'dir_two')
        self.path_mapping = [(os.path.join(TEST_DIR,'s129_air1.wav'),
                            os.path.join(TEST_DIR,'s129_beer1.wav'))]
        self.expected_val = 0.2266
        
    def test_dir_phon_sim(self):
        match_val = phonetic_similarity_directories(self.dir_one_path, self.dir_two_path)
        self.assertEqual(match_val,self.expected_val)
        
    def test_mapping_phon_sim(self):
        output_mapping = phonetic_similarity_mapping(self.path_mapping)
        self.assertEqual(output_mapping[0][2],self.expected_val)

if __name__ == '__main__':
    unittest.main()
