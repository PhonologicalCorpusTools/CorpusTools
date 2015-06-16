from collections import defaultdict, OrderedDict
from math import log2
import os

from corpustools.corpus.classes import EnvironmentFilter
from corpustools.exceptions import ProdError

def check_envs(corpus, envs, stop_check, call_back):
    """
    Search for the specified segments in the specified environments in
    the corpus.
"""

    env_matches = {env: {seg: 0 for seg in env.middle} for env in envs}

    missing_envs = defaultdict(set)
    overlapping_envs = defaultdict(dict)

    if call_back is not None:
        call_back('Finding instances of environments...')
        call_back(0,len(corpus))
        cur = 0
    for word in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)

        tier = getattr(word, corpus.sequence_type)
        overlaps = defaultdict(list)
        found_env = False
        for env in envs:
            a = env.is_applicable(tier.with_word_boundaries())
            if not a:
                continue
            es = tier.find(env)
            if es is not None:
                found_env = True
                for e in es:
                    env_matches[env][e.middle] += word.frequency
                    overlaps[e].append(env)


        if not found_env and any(m in tier for m in envs[0].middle):
            actual_env = tier.find_nonmatch(envs[0])
            missing_envs[str(actual_env)].update([str(word)])

        for k,v in overlaps.items():
            if len(v) > 1:
                k = tuple(str(env) for env in v)
                k2 = str(k)
                if k2 not in overlapping_envs[k]:
                    overlapping_envs[k][k2] = set()
                overlapping_envs[k][k2].update([str(word)])

    return env_matches, missing_envs, overlapping_envs

def calc_prod_all_envs(corpus, seg1, seg2, all_info = False, stop_check = None,
                call_back = None):
    """
    Main function for calculating predictability of distribution for
    two segments over a corpus, regardless of environment.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : string
        The first segment
    seg2 : string
        The second segment
    all_info : bool
        If true, all the intermediate numbers for calculating predictability
        of distribution will be returned.  If false, only the final entropy
        will be returned.  Defaults to False.

    Returns
    -------
    float or list
        A list of [entropy, frequency of environment, frequency of seg1,
        frequency of seg2] if all_info is True, or just entropy if
        all_info is False.
    """
    freq_base  = corpus.get_frequency_base()
    if stop_check is not None and stop_check():
        return
    seg1_count = freq_base[seg1]
    seg2_count = freq_base[seg2]
    total_count = seg1_count + seg2_count
    if total_count:
        H = -1 * ((seg1_count/total_count) * log2(seg1_count/total_count) + (seg2_count/total_count) * log2(seg2_count/total_count))
    else:
        H = 0.0
    if all_info:
        H = [H, total_count, seg1_count, seg2_count]
    return H


def calc_prod(corpus, envs, strict = True, all_info = False, stop_check = None,
                call_back = None):
    """
    Main function for calculating predictability of distribution for
    two segments over specified environments in a corpus.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    envs : list of EnvironmentFilter
        List of EnvironmentFilter objects that specify environments
    strict : bool
        If true, exceptions will be raised for non-exhausive environments
        and non-unique environments.  If false, only warnings will be
        shown.  Defaults to True.
    all_info : bool
        If true, all the intermediate numbers for calculating predictability
        of distribution will be returned.  If false, only the final entropy
        will be returned.  Defaults to False.

    Returns
    -------
    dictionary
        Keys are the environments specified and values are either a list
        of [entropy, frequency of environment, frequency of seg1, frequency
        of seg2] if all_info is True, or just entropy if all_info is False.
    """
    seg_list = envs[0].middle
    for e in envs:
        if e.middle != seg_list:
            raise(PCTError("Middle segments of all environments must be the same."))

    returned = check_envs(corpus, envs, stop_check, call_back)

    if stop_check is not None and stop_check():
        return
    env_matches, miss_envs, overlap_envs = returned
    if miss_envs or overlap_envs:
        if strict:
            raise(ProdError(envs, miss_envs, overlap_envs))

    H_dict = OrderedDict()

    #CALCULATE ENTROPY IN INDIVIDUAL ENVIRONMENTS FIRST
    total_matches = {x: 0 for x in seg_list}
    total_frequency = 0

    if call_back is not None:
        call_back('Calculating predictability of distribution...')
        call_back(0,len(corpus))
        cur = 0
    for env in env_matches:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            call_back(cur)
        total_tokens = 0
        matches = {}
        for seg in seg_list:
            matches[seg] = env_matches[env][seg]
            total_matches[seg] += matches[seg]
            total_tokens += matches[seg]
        total_frequency += total_tokens

        if not total_tokens:
            H = 0
        else:
            seg_H = {}
            for seg in seg_list:
                seg_prob = matches[seg] / total_tokens
                seg_H[seg] = log2(seg_prob)*seg_prob if seg_prob > 0 else 0
            H = sum(seg_H.values())*-1
            if not H:
                H = H+0 #avoid the -0.0 problem
        H_dict[env] = [H, total_tokens] + [matches[x] for x in seg_list]

    #CALCULATE WEIGHTED ENTROPY LAST
    weighted_H = 0
    for env in env_matches:
        weighted_H += H_dict[env][0] * (H_dict[env][1] / total_frequency) if total_frequency>0 else 0


    try:
        avg_h = sum(total_matches.values())/total_frequency
    except ZeroDivisionError:
        avg_h = 0.0

    H_dict['AVG'] = [weighted_H, avg_h] + [total_matches[x] for x in seg_list]

    if not all_info:
        for k,v in H_dict.items():
            H_dict[k] = v[0]
    return H_dict
