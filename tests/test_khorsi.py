import unittest

import sys
import os

from corpustools.symbolsim.khorsi import lcs
from corpustools.symbolsim.string_similarity import string_similarity
from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        WeightedVariantContext)

def test_freq_base_spelling_type(unspecified_test_corpus):
    expected = {'#':30,
                'a':16,
                'e':3,
                'h':8,
                'i':10,
                'm':6,
                'n':4,
                'o':4,
                's':13,
                'ʃ':1,
                't':11,
                'u':4,
                'total':110}

    with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'type') as c:
        freq_base = c.get_frequency_base()
    assert(freq_base == expected)

def test_freq_base_spelling_token(unspecified_test_corpus):
    expected = {'#': 1158,
                'a':466,
                'e':118,
                'h':538,
                'i':429,
                'm':156,
                'n':142,
                'o':171,
                's':856,
                'ʃ':2,
                't':271,
                'u':265,
                'total':4572}

    with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'token') as c:
        freq_base = c.get_frequency_base()
    assert(freq_base == expected)

def test_freq_base_transcription_type(unspecified_test_corpus):
    expected = {'#':30,
                'ɑ':16,
                'e':3,
                'i':10,
                'm':6,
                'n':4,
                'o':4,
                's':5,
                'ʃ':9,
                't':11,
                'u':4,
                'total':102}

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        freq_base = c.get_frequency_base()
    assert(freq_base == expected)

def test_freq_base_transcription_token(unspecified_test_corpus):
    expected = {'#': 1158,
                'ɑ':466,
                'e':118,
                'i':429,
                'm':156,
                'n':142,
                'o':171,
                's':318,
                'ʃ':540,
                't':271,
                'u':265,
                'total':4034}

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        freq_base = c.get_frequency_base()
    assert(freq_base == expected)

def test_lcs_spelling(unspecified_test_corpus):
    expected = [('atema','atema','atema',''),
                ('atema','enuta','e','atmatnua'),
                ('atema','mashomisi','ma','ateshomisi'),
                ('atema','mata','ma','ateta'),
                ('atema','nata','at','emana'),
                ('atema','sasi','a','temassi'),
                ('atema','shashi','a','temashshi'),
                ('atema','shisata','at','emashisa'),
                ('atema','shushoma','ma','ateshusho'),
                ('atema','ta','t','aemaa'),
                ('atema','tatomi','at','ematomi'),
                ('atema','tishenishu','t','aemaishenishu'),
                ('atema','toni','t','aemaoni'),
                ('atema','tusa','t','aemausa'),
                ('atema','ʃi','','atemaʃi'),
                ('sasi','atema','a','temassi'),
                ('sasi','enuta','a','ssienut'),
                ('sasi','mashomisi','as','simhomisi'),
                ('sasi','mata','a','ssimta'),
                ('sasi','nata','a','ssinta'),
                ('sasi','sasi','sasi',''),
                ('sasi','shashi','as','sishhi'),
                ('sasi','shisata','sa','sishita'),
                ('sasi','shushoma','s','asiahushom'),
                ('sasi','ta','a','ssit'),
                ('sasi','tatomi','a','ssittomi'),
                ('sasi','tishenishu','s','asitihenishu'),
                ('sasi','toni','i','saston'),
                ('sasi','tusa','sa','situ'),
                ('sasi','ʃi','i','sasʃ'),
                ]
    for v in expected:
        calced = lcs(list(v[0]),list(v[1]))
        calced = (sorted(calced[0]),sorted(calced[1]))
        assert(calced == (sorted(v[2]),sorted(v[3])))

def test_lcs_transcription(unspecified_test_corpus):
    expected = [('atema','atema',['ɑ','t','e','m','ɑ'],[]),
                ('atema','enuta',['e'],['ɑ','t','m','ɑ','t','n','u','ɑ']),
                ('atema','mashomisi',['m','ɑ'],['ɑ','t','e','ʃ','o','m','i','s','i']),
                ('atema','mata',['m','ɑ'],['ɑ','t','e','t','ɑ']),
                ('atema','nata',['ɑ','t'],['e','m','ɑ','n','ɑ']),
                ('atema','sasi',['ɑ'],['t','e','m','ɑ','s','s','i']),
                ('atema','shashi',['ɑ'],['t','e','m','ɑ','ʃ','ʃ','i']),
                ('atema','shisata',['ɑ','t'],['e','m','ɑ','ʃ','i','s','ɑ']),
                ('atema','shushoma',['m','ɑ'],['ɑ','t','e','ʃ','u','ʃ','o']),
                ('atema','ta',['t'],['ɑ','e','m','ɑ','ɑ']),
                ('atema','tatomi',['ɑ','t'],['e','m','ɑ','t','o','m','i']),
                ('atema','tishenishu',['t'],['ɑ','e','m','ɑ','i','ʃ','e','n','i','ʃ','u']),
                ('atema','toni',['t'],['ɑ','e','m','ɑ','o','n','i']),
                ('atema','tusa',['t'],['ɑ','e','m','ɑ','u','s','ɑ']),
                ('atema','ʃi',[],['ɑ','t','e','m','ɑ','ʃ','i']),
                ('sasi','atema',['ɑ'],['t','e','m','ɑ','s','s','i']),
                ('sasi','enuta',['ɑ'],['s','s','i','e','n','u','t']),
                ('sasi','mashomisi',['s','i'],['s','ɑ','m','ɑ','ʃ','o','m','i']),
                ('sasi','mata',['ɑ'],['s','s','i','m','t','ɑ']),
                ('sasi','nata',['ɑ'],['s','s','i','n','t','ɑ']),
                ('sasi','sasi',['s','ɑ','s','i'],[]),
                ('sasi','shashi',['ɑ'],['s','s','i','ʃ','ʃ','i']),
                ('sasi','shisata',['s','ɑ'],['s','i','ʃ','i','t','ɑ']),
                ('sasi','shushoma',['ɑ'],['s','s','i','ʃ','u','ʃ','o','m']),
                ('sasi','ta',['ɑ'],['s','s','i','t']),
                ('sasi','tatomi',['ɑ'],['s','s','i','t','t','o','m','i']),
                ('sasi','tishenishu',['i'],['s','ɑ','s','t','ʃ','e','n','i','ʃ','u']),
                ('sasi','toni',['i'],['s','ɑ','s','t','o','n']),
                ('sasi','tusa',['s','ɑ'],['s','i','t','u']),
                ('sasi','ʃi',['i'],['s','ɑ','s','ʃ']),
                ]
    for v in expected:
        x1 = unspecified_test_corpus[v[0]].transcription
        x2 = unspecified_test_corpus[v[1]].transcription
        calced = lcs(x1,x2)
        calced = (calced[0],sorted(calced[1]))
        assert(calced == (v[2],sorted(v[3])))


def test_mass_relate_spelling_type(unspecified_test_corpus):
    expected = [(unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('atema'),11.0766887),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('enuta'),-14.09489383),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mashomisi'),-18.35890071),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mata'),-6.270847817),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('nata'),-8.494720336),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('sasi'),-13.57140897),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shashi'),-18.17657916),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shisata'),-13.51516925),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shushoma'),-16.90806783),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ta'),-8.717863887),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tatomi'),-13.53912249),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tishenishu'),-28.78151269),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('toni'),-15.17933206),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tusa'),-13.53067344),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ʃi'),-17.53815687),]
    expected.sort(key=lambda t:t[2])
    expected.reverse()
    with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'type') as c:
        calced = string_similarity(c, unspecified_test_corpus.find('atema'), 'khorsi')
    for i, v in enumerate(expected):
        assert(abs(calced[i][2] - v[2]) < 0.0001)

    expected = [(unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('atema'),-13.57140897),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('enuta'),-15.36316844),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mashomisi'),-16.92481569),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mata'),-10.28799462),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('nata'),-10.69345973),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('sasi'),7.323034009),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shashi'),-8.971692634),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shisata'),-10.26267682),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shushoma'),-20.30229654),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ta'),-6.088289546),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tatomi'),-15.73786189),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tishenishu'),-25.52902026),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('toni'),-11.13974683),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tusa'),-5.449867265),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ʃi'),-7.54617756),]
    expected.sort(key=lambda t:t[2])
    expected.reverse()
    with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'type') as c:
        calced = string_similarity(c, unspecified_test_corpus.find('sasi'),'khorsi')
    for i, v in enumerate(expected):
        assert(abs(calced[i][2] - v[2]) < 0.0001)

def test_mass_relate_spelling_token(unspecified_test_corpus):
    expected = [(unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('atema'),12.9671688),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('enuta'),-16.49795651),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mashomisi'),-17.65533907),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mata'),-7.337667817),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('nata'),-9.088485208),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('sasi'),-13.8251823),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shashi'),-17.52074498),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shisata'),-12.59737574),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shushoma'),-14.82488063),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ta'),-9.8915809),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tatomi'),-14.6046824),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tishenishu'),-27.61147254),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('toni'),-16.14809881),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tusa'),-13.8308605),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ʃi'),-22.4838445)]
    expected.sort(key=lambda t:t[2])
    expected.reverse()
    with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'token') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('atema'),'khorsi')
    for i, v in enumerate(expected):
        assert(abs(calced[i][2] - v[2]) < 0.0001)

    expected = [(unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('atema'),-13.8251823),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('enuta'),-14.48366705),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mashomisi'),-16.62778969),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mata'),-10.46022702),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('nata'),-10.55425597),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('sasi'),6.832376308),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shashi'),-7.235843913),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shisata'),-9.913037922),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shushoma'),-19.77169406),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ta'),-5.382988852),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tatomi'),-16.07045316),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tishenishu'),-24.92713472),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('toni'),-11.39132061),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tusa'),-5.172159875),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ʃi'),-10.12650306)]
    expected.sort(key=lambda t:t[2])
    expected.reverse()
    with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'token') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('sasi'),'khorsi')
    for i, v in enumerate(expected):
        assert(abs(calced[i][2] - v[2]) < 0.0001)

def test_mass_relate_transcription_type(unspecified_test_corpus):
    expected = [(unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('atema'),10.54988612),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('enuta'),-13.35737022),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mashomisi'),-16.64202823),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mata'),-5.95476627),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('nata'),-8.178638789),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('sasi'),-14.85026877),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shashi'),-13.67469544),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shisata'),-12.0090178),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shushoma'),-12.51154463),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ta'),-8.296421824),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tatomi'),-13.01231991),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tishenishu'),-23.85818691),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('toni'),-14.54716897),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tusa'),-13.85402179),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ʃi'),-14.60340869),]
    expected.sort(key=lambda t:t[2])
    expected.reverse()
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('atema'),'khorsi')
    for i, v in enumerate(expected):
        assert(abs(calced[i][2] - v[2]) < 0.0001)

    expected = [(unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('atema'),-14.85026877),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('enuta'),-16.64202823),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mashomisi'),-12.94778139),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mata'),-11.67221494),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('nata'),-12.07768004),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('sasi'),8.812614836),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shashi'),-11.93742415),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shisata'),-7.90637444),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shushoma'),-18.22899329),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ta'),-7.683230889),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tatomi'),-16.91136117),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tishenishu'),-21.83498509),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('toni'),-12.52396715),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tusa'),-5.239146233),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ʃi'),-6.943894326),]
    expected.sort(key=lambda t:t[2])
    expected.reverse()
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('sasi'),'khorsi')
    for i, v in enumerate(expected):
        assert(abs(calced[i][2] - v[2]) < 0.0001)

def test_mass_relate_transcription_token(unspecified_test_corpus):
    expected = [(unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('atema'),12.10974787),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('enuta'),-15.29756722),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mashomisi'),-16.05808867),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mata'),-8.574032654),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('nata'),-6.823215263),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('sasi'),-14.77671518),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shashi'),-13.71767966),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shisata'),-11.34309371),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shushoma'),-11.19329949),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ta'),-9.205644162),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tatomi'),-13.74726148),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tishenishu'),-23.12247048),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('toni'),-15.1191937),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tusa'),-13.79217439),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ʃi'),-15.68503325),]
    expected.sort(key=lambda t:t[2])
    expected.reverse()
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('atema'),'khorsi')
    for i, v in enumerate(expected):
        assert(abs(calced[i][2] - v[2]) < 0.0001)

    expected = [(unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('atema'),-14.77671518),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('enuta'),-15.43519993),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mashomisi'),-13.96361833),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mata'),-11.58324408),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('nata'),-11.67727303),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('sasi'),8.126877557),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shashi'),-9.734809346),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shisata'),-7.840021077),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shushoma'),-15.95332831),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ta'),-6.848974285),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tatomi'),-16.85050186),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tishenishu'),-20.51761446),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('toni'),-12.51433768),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tusa'),-4.829191506),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ʃi'),-5.994066536),]
    expected.sort(key=lambda t:t[2])
    expected.reverse()
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('sasi'),'khorsi')
    for i, v in enumerate(expected):
        assert(abs(calced[i][2] - v[2]) < 0.0001)
