
import sys
import os

from corpustools.prod.pred_of_dist import check_envs, calc_prod, count_segs


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
    result = calc_prod(specified_test_corpus,seg1,seg2,env_list,tier, type_or_token)
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
    result = calc_prod(specified_test_corpus,seg1,seg2,env_list,tier, type_or_token,all_info=False)
    for k,v in result.items():
        k = str(k).replace("'",'').replace(' ','')
        assert(expected[k]-v < 0.001)

