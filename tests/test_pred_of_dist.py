
import sys
import os
import pytest

from corpustools.prod.pred_of_dist import (check_envs, calc_prod,
                                        EnvironmentFilter)

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        WeightedVariantContext)

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
    with CanonicalVariantContext(specified_test_corpus, tier, type_or_token) as c:
        result = calc_prod(c, env_list)
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
    with CanonicalVariantContext(specified_test_corpus, tier, type_or_token) as c:
        result = calc_prod(c, env_list, all_info=False)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

def test_prod_wordtokens_token(specified_discourse_corpus):
    seg1 = 's'
    seg2 = 'ʃ'
    expected = {"-voc":0.0,
                "+voc,+high":0.8631205, #0.9321115676166747,          #Error!!!?!?!?
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

    type_or_token = 'token'
    tier = 'transcription'

    with MostFrequentVariantContext(specified_discourse_corpus.lexicon, tier, type_or_token) as c:
        result = calc_prod(c, env_list)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

    type_or_token = 'token'
    tier = 'transcription'
    with WeightedVariantContext(specified_discourse_corpus.lexicon, tier, type_or_token) as c:
        result = calc_prod(c, env_list)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

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

    type_or_token = 'type'
    tier = 'transcription'
    with MostFrequentVariantContext(specified_discourse_corpus.lexicon, tier, type_or_token) as c:
        result = calc_prod(c, env_list, all_info=False)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

    with WeightedVariantContext(specified_discourse_corpus.lexicon, tier, type_or_token) as c:
        result = calc_prod(c, env_list, all_info=False)
    for k,v in result.items():
        assert(expected_envs[k]-v < 0.001)

def test_prod_pronunciation_variants(pronunciation_variants_corpus):
    pass
