import unittest

class RuntimeTest(unittest.TestCase):
    def setUp(self):
        self.dir_one_path = r'C:\Users\michael\Documents\Testing\dir_one'
        self.dir_two_path = r'C:\Users\michael\Documents\Testing\dir_two'
        self.path_mapping = [(r'C:\Users\michael\Documents\Testing\s129_air1.wav',
                            r'C:\Users\michael\Documents\Testing\s129_beer1.wav')]
        self.expected_val = 0.2266
        
    def test_dir_phon_sim(self):
        pass
        
    def test_mapping_phon_sim(self):
        pass
