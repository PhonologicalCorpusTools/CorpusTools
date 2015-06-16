
import sys
import os
import pytest

from corpustools.prod.pred_of_dist import (check_envs, calc_prod, count_segs,
                                        calc_prod_wordtokens, EnvironmentFilter)


def test_prod_allenvs(specified_test_corpus):
    return

def test_prod_token(specified_test_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"-voc":0.0,
                "+voc,+high":0.9321115676166747,
                "+voc,-high":0.9660096062568557,
                "#":0.0}
    env_list = []
    expected_envs = {}
    for k, v in expected.items():
        if k != '#':
            segs = specified_test_corpus.features_to_segments(k)
        else:
            segs = k
        env = EnvironmentFilter(['s', 'ʃ'], None, [segs])
        env_list.append(env)
        expected_envs[env] = v
    expected_envs["AVG"] = 0.9241743523004413
    type_or_token = 'token'
    tier = 'transcription'
    result = calc_prod(specified_test_corpus,env_list,tier, type_or_token)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

def test_prod_type(specified_test_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"-voc":0.0,
                "+voc,+high":0.863120568566631,
                "+voc,-high":0.9852281360342515,
                "#":0.0}
    env_list = []
    expected_envs = {}
    for k, v in expected.items():
        if k != '#':
            segs = specified_test_corpus.features_to_segments(k)
        else:
            segs = k
        env = EnvironmentFilter(['s', 'ʃ'], None, [segs])
        env_list.append(env)
        expected_envs[env] = v
    expected_envs["AVG"] = 0.9241743523004413
    type_or_token = 'type'
    tier = 'transcription'
    result = calc_prod(specified_test_corpus,env_list, tier, type_or_token,all_info=False)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

@pytest.mark.xfail
def test_prod_wordtokens_token(specified_discourse_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"-voc":0.0,
                "+voc,+high":0.9321115676166747,
                "+voc,-high":0.9660096062568557,
                "#":0.0}
    env_list = []
    expected_envs = {}
    for k, v in expected.items():
        if k != '#':
            segs = specified_discourse_corpus.lexicon.features_to_segments(k)
        else:
            segs = k
        env = EnvironmentFilter(['s', 'ʃ'], None, [segs])
        env_list.append(env)
        expected_envs[env] = v
    expected_envs["AVG"] = 0.9241743523004413

    type_or_token = 'most_frequent_token'
    tier = 'transcription'
    result = calc_prod_wordtokens(specified_discourse_corpus.lexicon,env_list,tier, type_or_token)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

    type_or_token = 'count_token'
    tier = 'transcription'
    result = calc_prod_wordtokens(specified_discourse_corpus.lexicon,env_list,tier, type_or_token)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

@pytest.mark.xfail
def test_prod_wordtokens_type(specified_discourse_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"-voc":0.0,
                "+voc,+high":0.863120568566631,
                "+voc,-high":0.9852281360342515,
                "#":0.0}
    env_list = []
    expected_envs = {}
    for k, v in expected.items():
        if k != '#':
            segs = specified_discourse_corpus.lexicon.features_to_segments(k)
        else:
            segs = k
        env = EnvironmentFilter(['s', 'ʃ'], None, [segs])
        env_list.append(env)
        expected_envs[env] = v
    expected_envs["AVG"] = 0.9241743523004413

    type_or_token = 'most_frequent_type'
    tier = 'transcription'
    result = calc_prod_wordtokens(specified_discourse_corpus.lexicon,env_list,tier, type_or_token,all_info=False)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

    type_or_token = 'relative_type'
    tier = 'transcription'
    result = calc_prod_wordtokens(specified_discourse_corpus.lexicon,env_list,tier, type_or_token,all_info=False)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

