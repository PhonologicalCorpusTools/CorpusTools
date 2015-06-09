
import sys
import os

from corpustools.prod.pred_of_dist import (check_envs, calc_prod, count_segs,
                                        calc_prod_wordtokens)

from corpustools.contextmanagers import CanonicalVariantContext, MostFrequentVariantContext

def test_prod_allenvs(specified_test_corpus):
    return

def test_prod_token(specified_test_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"_[-voc]":0.0,
                "_[+voc,+high]":0.9321115676166747,
                "_[+voc,-high]":0.9660096062568557,
                "_#":0.0}
    env_list = list(expected.keys())
    expected["AVG"] = 0.9496532099899153
    type_or_token = 'token'
    tier = 'transcription'
    with CanonicalVariantContext(specified_test_corpus, tier, type_or_token) as c:
        result = calc_prod(c, seg1, seg2, env_list)
    for k,v in result.items():
        k = str(k).replace("'",'').replace(' ','')
        assert(expected[k]-v < 0.001)

def test_prod_type(specified_test_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"_[-voc]":0.0,
                "_[+voc,+high]":0.863120568566631,
                "_[+voc,-high]":0.9852281360342515,
                "_#":0.0}
    env_list = list(expected.keys())
    expected["AVG"] = 0.9241743523004413
    type_or_token = 'type'
    tier = 'transcription'
    with CanonicalVariantContext(specified_test_corpus, tier, type_or_token) as c:
        result = calc_prod(c, seg1, seg2, env_list, all_info=False)
    for k,v in result.items():
        k = str(k).replace("'",'').replace(' ','')
        assert(expected[k]-v < 0.001)

def test_prod_wordtokens_token(specified_discourse_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"_[-voc]":0.0,
                "_[+voc,+high]":0.9321115676166747,
                "_[+voc,-high]":0.9660096062568557,
                "_#":0.0}
    env_list = list(expected.keys())
    expected["AVG"] = 0.9496532099899153

    type_or_token = 'most_frequent_token'
    tier = 'transcription'
    result = calc_prod_wordtokens(specified_discourse_corpus.lexicon,seg1,seg2,env_list,tier, type_or_token)
    for k,v in result.items():
        k = str(k).replace("'",'').replace(' ','')
        assert(expected[k]-v < 0.001)

    type_or_token = 'count_token'
    tier = 'transcription'
    result = calc_prod_wordtokens(specified_discourse_corpus.lexicon,seg1,seg2,env_list,tier, type_or_token)
    for k,v in result.items():
        k = str(k).replace("'",'').replace(' ','')
        assert(expected[k]-v < 0.001)

def test_prod_wordtokens_type(specified_discourse_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"_[-voc]":0.0,
                "_[+voc,+high]":0.863120568566631,
                "_[+voc,-high]":0.9852281360342515,
                "_#":0.0}
    env_list = list(expected.keys())
    expected["AVG"] = 0.9241743523004413

    type_or_token = 'most_frequent_type'
    tier = 'transcription'
    result = calc_prod_wordtokens(specified_discourse_corpus.lexicon,seg1,seg2,env_list,tier, type_or_token,all_info=False)
    for k,v in result.items():
        k = str(k).replace("'",'').replace(' ','')
        assert(expected[k]-v < 0.001)

    type_or_token = 'relative_type'
    tier = 'transcription'
    result = calc_prod_wordtokens(specified_discourse_corpus.lexicon,seg1,seg2,env_list,tier, type_or_token,all_info=False)
    for k,v in result.items():
        k = str(k).replace("'",'').replace(' ','')
        assert(expected[k]-v < 0.001)

