
import sys
import os

from corpustools.freqalt.freq_of_alt import calc_freq_of_alt
from corpustools.contextmanagers import (CanonicalVariantContext,
                                            MostFrequentVariantContext)

def test_freqalt(specified_test_corpus):
    with CanonicalVariantContext(specified_test_corpus, 'transcription', 'type') as c:

        result = calc_freq_of_alt(c,'s','ʃ','khorsi', min_rel = -15, phono_align=True)
        assert(result==(8,3,0.375))

        result = calc_freq_of_alt(c,'s','ʃ','khorsi', min_rel = -6, phono_align=True)
        assert(result==(8,0,0))

        result = calc_freq_of_alt(c,'s','ʃ','khorsi', min_rel = -6, phono_align=False)
        assert(result==(8,2,0.25))

        result = calc_freq_of_alt(c,'s','ʃ','khorsi', min_rel = -15, phono_align=False)
        assert(result==(8,7,0.875))

        result = calc_freq_of_alt(c,'s','ʃ','edit_distance', max_rel = 2, phono_align=True)
        assert(result==(8,2,0.25))

        result = calc_freq_of_alt(c,'s','ʃ','edit_distance', max_rel = 2, phono_align=False)
        assert(result==(8,2,0.25))

        result = calc_freq_of_alt(c,'s','ʃ','phono_edit_distance', max_rel = 6, phono_align=True)
        assert(result==(8,2,0.25))

        result = calc_freq_of_alt(c,'s','ʃ','phono_edit_distance', max_rel = 6, phono_align=False)
        assert(result==(8,2,0.25))

    with CanonicalVariantContext(specified_test_corpus, 'transcription', 'token') as c:

        result = calc_freq_of_alt(c,'s','ʃ','khorsi', min_rel = -15, phono_align=True)
        assert(result==(8,3,0.375))

        result = calc_freq_of_alt(c,'s','ʃ','khorsi', min_rel = -6, phono_align=True)
        assert(result==(8,2,0.25))

        result = calc_freq_of_alt(c,'s','ʃ','khorsi', min_rel = -15, phono_align=False)
        assert(result==(8,7,0.875))

        result = calc_freq_of_alt(c,'s','ʃ','khorsi', min_rel = -6, phono_align=False)
        assert(result==(8,3,0.375))

        result = calc_freq_of_alt(c,'s','ʃ','edit_distance', max_rel = 4, phono_align=True)
        assert(result==(8,3,0.375))

        result = calc_freq_of_alt(c,'s','ʃ','edit_distance', max_rel = 4, phono_align=False)
        assert(result==(8,6,0.75))

        result = calc_freq_of_alt(c,'s','ʃ','phono_edit_distance', max_rel = 20, phono_align=True)
        assert(result==(8,3,0.375))

        result = calc_freq_of_alt(c,'s','ʃ','phono_edit_distance', max_rel = 20, phono_align=False)
        assert(result==(8,6,0.75))
