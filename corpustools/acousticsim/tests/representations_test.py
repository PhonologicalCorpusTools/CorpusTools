

from numpy import array,sum,sqrt
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,corpustools_path)
from corpustools.acousticsim.representations import (to_envelopes,
                                    to_mfcc,
                                    preproc)

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

TEST_DIR = r'C:\Users\michael\Documents\Testing\acoustic_similarity'

filenames = ['s01_s0101a_big_910','s01_s0101a_care_1188',
            's01_s0101a_chief_831','s01_s0101a_choose_1149',
            's01_s0101a_come_340','s01_s0101a_dad_497',
            's01_s0101a_good_412','s01_s0101a_hall_99']

class EnvelopeTest(unittest.TestCase):
    def setUp(self):
        self.num_bands = 4
        self.freq_lims = (80,7800)



    def test_envelope_gen(self):
        if not os.path.exists(TEST_DIR):
            return
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_lewandowski_env.mat')
            m = loadmat(matpath)
            env = to_envelopes(wavpath, self.num_bands,self.freq_lims)
            for i in range(self.num_bands):
                denom = sqrt(sum(env[:,i]**2))
                env[:,i] = env[:,i]/denom
            assert_array_almost_equal(m['env1'],env)


class MfccTest(unittest.TestCase):
    def setUp(self):
        self.numCC = 13
        self.winLen = 0.025
        self.timeStep = 0.01
        self.freq_lims = (0,8000)
        self.num_filters = 20

    def test(self):
        if not os.path.exists(TEST_DIR):
            return
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_mfcc.mat')
            m = loadmat(matpath)
            mfcc,pspec,aspec = to_mfcc(wavpath,self.freq_lims,self.numCC,self.winLen,
                                    self.timeStep,num_filters=self.num_filters,
                                    debug = True,
                                    use_power=True
                                    )
            assert_array_almost_equal(m['aspectrum'].T,aspec,decimal=4)
            assert_array_almost_equal(m['cepstra'].T,mfcc)

if __name__ == '__main__':
    unittest.main()
