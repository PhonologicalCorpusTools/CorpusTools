
import sys
import os

from corpustools.freqalt.freq_of_alt import calc_freq_of_alt

def test_freqalt(specified_test_corpus):
    result = calc_freq_of_alt(specified_test_corpus,'s','ʃ','khorsi','type', min_rel = -15,
                                phono_align=True)
    assert(result==(8,3,0.375))

    result = calc_freq_of_alt(specified_test_corpus,'s','ʃ','khorsi','token', min_rel = -15,
                                phono_align=True)
    assert(result==(8,3,0.375))

    result = calc_freq_of_alt(specified_test_corpus,'s','ʃ','khorsi','type', min_rel = -6,
                                phono_align=True)
    assert(result==(8,0,0))

    result = calc_freq_of_alt(specified_test_corpus,'s','ʃ','khorsi','token', min_rel = -6,
                                phono_align=True)
    assert(result==(8,2,0.25))

    result = calc_freq_of_alt(specified_test_corpus,'s','ʃ','khorsi','type', min_rel = -15,
                                phono_align=False)
    assert(result==(8,7,0.875))

    result = calc_freq_of_alt(specified_test_corpus,'s','ʃ','khorsi','token', min_rel = -15,
                                phono_align=False)
    assert(result==(8,7,0.875))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','type', min_rel = -6,
                                phono_align=False)
    assert(result==(8,2,0.25))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','khorsi','token', min_rel = -6,
                                phono_align=False)
    assert(result==(8,3,0.375))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','edit_distance','type', max_rel = 2,
                                phono_align=True)
    assert(result==(8,2,0.25))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','edit_distance','token', max_rel = 4,
                                phono_align=True)
    assert(result==(8,3,0.375))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','edit_distance','type', max_rel = 2,
                                phono_align=False, output_filename='nov4tests.txt')
    assert(result==(8,2,0.25))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','edit_distance','token', max_rel = 4,
                                phono_align=False)
    assert(result==(8,6,0.75))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','phono_edit_distance','type', max_rel = 6,
                                phono_align=True)
    assert(result==(8,2,0.25))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','phono_edit_distance','token', max_rel = 20,
                                phono_align=True)
    assert(result==(8,3,0.375))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','phono_edit_distance','type', max_rel = 6,
                                phono_align=False)
    assert(result==(8,2,0.25))

    result = calc_freq_of_alt(self.corpus,'s','ʃ','phono_edit_distance','token', max_rel = 20,
                                phono_align=False)
    assert(result==(8,6,0.75))

