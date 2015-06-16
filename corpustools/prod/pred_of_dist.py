from collections import defaultdict, OrderedDict
from math import log2
import os

from corpustools.corpus.classes import EnvironmentFilter

from corpustools.exceptions import ProdError

def count_segs_wordtokens(corpus, seg1, seg2, sequence_type, type_or_token, stop_check, call_back):
    """
    Count the frequency of segments in a corpus, for internal use as
    part of calculating predictability of distribution, using pronunciation
    variants of words.

    The supported frequency options are as follows: `most_frequent_type`
    selects the most frequent pronunciation variant as the transcription and uses the type
    frequency of the word; `most_frequent_token` does the same thing as
    `most_frequent_type` but uses the token frequency of the word;
    `count_token` treats each pronunciation variant as its own transcription
    and uses the token frequency of each variant; `relative_type` is similar
    to `count_token`, but the frequencies are normalized by the overall
    frequency of the word, yielding a type-like frequency.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : str
        First segment to count
    seg2 : str
        Second segment to count
    sequence_type : str
        Tier to count on
    type_or_token : str {'most_frequent_type', 'most_frequent_token', 'count_token', 'relative_type'}
        Specifies what kind of frequency to use in
        calculating predictability of distribution
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    float
        Count of the first segment
    float
        Count of the second segment
    """
    #type_or_token is one of: ['count_token', 'relative_type', 'most_frequent_type', 'most_frequent_token']

    seg1_counts = 0
    seg2_counts = 0

    if call_back is not None:
        call_back('Finding instances of segments...')
        call_back(0,len(corpus))
        cur = 0
    for word in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 20 == 0:
                call_back(cur)

        variants = word.variants(sequence_type)
        if len(variants.keys()) == 0:
            continue
        if type_or_token == 'count_token' or type_or_token == 'relative_type':
            if type_or_token == 'relative_type':
                f_total = sum(variants.values())

            for v, f in variants.items():
                if type_or_token == 'relative_type':
                    f /= f_total
                if seg1 in v:
                    seg1_counts += f
                if seg2 in v:
                    seg2_counts += f

        elif type_or_token.startswith('most_frequent'):
            tier = max(variants.keys(), key=(lambda key: variants[key]))
            if seg1 in tier:
                if type_or_token.endswith('type'):
                    seg1_counts += 1
                else:
                    seg1_counts += word.frequency
            if seg2 in tier:
                if type_or_token.endswith('type'):
                    seg2_counts += 1
                else:
                    seg2_counts += word.frequency
    return seg1_counts, seg2_counts

def count_segs(corpus, seg1, seg2, sequence_type, type_or_token, stop_check, call_back):
    """
    Count the frequency of segments in a corpus, for internal use as
    part of calculating predictability of distribution.

    DEPRECIATED in favor of using `make_freq_base` of the corpus object

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : str
        First segment to count
    seg2 : str
        Second segment to count
    sequence_type : str
        Tier to count on
    type_or_token : str {'type', 'token'}
        Flag for using 'type' freqency or 'token' frequency
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    float
        Count of the first segment
    float
        Count of the second segment
    """
    seg1_counts = 0
    seg2_counts = 0

    if call_back is not None:
        call_back('Finding instances of segments...')
        call_back(0,len(corpus))
        cur = 0
    for word in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        tier = getattr(word, sequence_type)
        for seg in tier:
            if seg == seg1:
                if type_or_token == 'type':
                    seg1_counts += 1
                else:
                    seg1_counts += word.frequency
            elif seg == seg2:
                if type_or_token == 'type':
                    seg2_counts += 1
                else:
                    seg2_counts += word.frequency
    return seg1_counts, seg2_counts

def check_envs_wordtokens(corpus, envs, sequence_type,
                            type_or_token, stop_check, call_back):
    """
    Search for the specified segments in the specified environments in
    the corpus.

    The supported frequency options are as follows: `most_frequent_type`
    selects the most frequent pronunciation variant as the transcription and uses the type
    frequency of the word; `most_frequent_token` does the same thing as
    `most_frequent_type` but uses the token frequency of the word;
    `count_token` treats each pronunciation variant as its own transcription
    and uses the token frequency of each variant; `relative_type` is similar
    to `count_token`, but the frequencies are normalized by the overall
    frequency of the word, yielding a type-like frequency.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : str
        First segment to count
    seg2 : str
        Second segment to count
    envs : list
        List of environment specification to search
    sequence_type : str
        Tier to search on
    type_or_token : str {'most_frequent_type', 'most_frequent_token', 'count_token', 'relative_type'}
        Specifies what kind of frequency to use in
        calculating predictability of distribution
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    dict
        Dictionary of frequencies of each segment in each environment
    dict
        Dictionary of environments found but not specified and the words
        they were found in
    dict
        Dictionary of environments that overlap with the words they were
        found in
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
            if cur % 20 == 0:
                call_back(cur)
        variants = word.variants(sequence_type)
        if len(variants.keys()) == 0:
            continue
        if type_or_token == 'count_token' or type_or_token == 'relative_type':
            if type_or_token == 'relative_type':
                f_total = sum(variants.values())
            for v, f in variants.items():
                if type_or_token == 'relative_type':
                    f /= f_total
                for pos, seg in enumerate(v):
                    if not (seg == seg1 or seg == seg2):
                        continue
                    tier_env = v.get_env(pos)
                    found_env_match = list()
                    for env in envs:
                        if tier_env in env:
                            env_matches[env][seg] += f
                            found_env_match.append(env)

                    if not found_env_match:
                        #found and environemnts with segs the user wants, but in
                        #an environement that was not supplied. Alert the user
                        #about this later
                        missing_envs[str(tier_env)].update([str(word)])

                    elif len(found_env_match) > 1:
                        #the user supplied environmnets that overlap, e.g. they want
                        #_[-voice] and also _k, but we shouldn't count this twice
                        #alert the user about this later
                        k = tuple(str(env) for env in found_env_match)
                        k2 = str(tier_env)
                        if k2 not in overlapping_envs[k]:
                            overlapping_envs[k][k2] = set()
                        overlapping_envs[k][k2].update([str(word)])

        elif type_or_token.startswith('most_frequent'):
            tier = max(variants.keys(), key=(lambda key: variants[key]))
            for pos,seg in enumerate(tier):
                if not (seg == seg1 or seg == seg2):
                    continue

                tier_env = tier.get_env(pos)
                found_env_match = list()
                for env in envs:
                    if tier_env in env:
                        if type_or_token.endswith('type'):
                            value = 1
                        elif type_or_token.endswith('token'):
                            value = word.frequency
                        env_matches[env][seg] += value
                        found_env_match.append(env)

                if not found_env_match:
                    #found and environemnts with segs the user wants, but in
                    #an environement that was not supplied. Alert the user
                    #about this later
                    missing_envs[str(tier_env)].update([str(word)])

                elif len(found_env_match) > 1:
                    #the user supplied environmnets that overlap, e.g. they want
                    #_[-voice] and also _k, but we shouldn't count this twice
                    #alert the user about this later
                    k = tuple(str(env) for env in found_env_match)
                    k2 = str(tier_env)
                    if k2 not in overlapping_envs[k]:
                        overlapping_envs[k][k2] = set()
                    overlapping_envs[k][k2].update([str(word)])

    return env_matches, missing_envs, overlapping_envs

def check_envs(corpus, envs, sequence_type,
                    type_or_token, stop_check, call_back):
    """
    Search for the specified segments in the specified environments in
    the corpus.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : str
        First segment to count
    seg2 : str
        Second segment to count
    envs : list
        List of environment specification to search
    sequence_type : str
        Tier to search on
    type_or_token : str {'type', 'token'}
        Specifies what kind of frequency to use in
        calculating predictability of distribution
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    dict
        Dictionary of frequencies of each segment in each environment
    dict
        Dictionary of environments found but not specified and the words
        they were found in
    dict
        Dictionary of environments that overlap with the words they were
        found in
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
            if cur % 20 == 0:
                call_back(cur)
        tier = getattr(word, sequence_type)
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
                    if type_or_token == 'type':
                        value = 1
                    elif type_or_token == 'token':
                        value = word.frequency
                    env_matches[env][e.middle] += value
                    overlaps[e].append(env)


        if not found_env and any(m in tier for m in envs[0].middle):
            #found and environemnts with segs the user wants, but in
            #an environement that was not supplied. Alert the user
            #about this later
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

def calc_prod_wordtokens_all_envs(corpus, seg1, seg2, sequence_type = 'transcription',
                type_or_token = 'most_frequent_type', all_info = False, stop_check = None,
                call_back = None):
    """
    Main function for calculating predictability of distribution for
    two segments over a corpus, regardless of environment, using pronunciation
    variants of words.

    The supported frequency options are as follows: `most_frequent_type`
    selects the most frequent pronunciation variant as the transcription and uses the type
    frequency of the word; `most_frequent_token` does the same thing as
    `most_frequent_type` but uses the token frequency of the word;
    `count_token` treats each pronunciation variant as its own transcription
    and uses the token frequency of each variant; `relative_type` is similar
    to `count_token`, but the frequencies are normalized by the overall
    frequency of the word, yielding a type-like frequency.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : str
        The first segment
    seg2 : str
        The second segment
    sequence_type : str
        Name of the Corpus tier to use for finding environments, defaults
        to 'transcription'
    type_or_token : str {'most_frequent_type', 'most_frequent_token', 'count_token', 'relative_type'}
        Specifies what kind of frequency to use in
        calculating predictability of distribution
    all_info : bool
        If true, all the intermediate numbers for calculating predictability
        of distribution will be returned.  If false, only the final entropy
        will be returned.  Defaults to False.
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    float or list
        A list of [entropy, frequency of environment, frequency of seg1,
        frequency of seg2] if all_info is True, or just entropy if
        all_info is False.
    """
    returned  = count_segs_wordtokens(corpus, seg1, seg2, sequence_type,
                                    type_or_token, stop_check, call_back)
    if stop_check is not None and stop_check():
        return
    seg1_count, seg2_count = returned
    total_count = seg1_count + seg2_count
    if total_count:
        H = -1 * ((seg1_count/total_count) * log2(seg1_count/total_count) \
                    + (seg2_count/total_count) * log2(seg2_count/total_count))
    else:
        H = 0.0
    if all_info:
        H = [H, total_count, seg1_count, seg2_count]
    return H

def calc_prod_all_envs(corpus, seg1, seg2, sequence_type = 'transcription',
                type_or_token = 'type', all_info = False, stop_check = None,
                call_back = None):
    """
    Main function for calculating predictability of distribution for
    two segments over a corpus, regardless of environment.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : str
        The first segment
    seg2 : str
        The second segment
    sequence_type : str
        Name of the Corpus tier to use for finding environments, defaults
        to 'transcription'
    type_or_token : str {'type', 'token'}
        Specify whether to use type frequency or token frequency in
        calculating predictability of distribution
    all_info : bool
        If true, all the intermediate numbers for calculating predictability
        of distribution will be returned.  If false, only the final entropy
        will be returned.  Defaults to False.
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    float or list
        A list of [entropy, frequency of environment, frequency of seg1,
        frequency of seg2] if all_info is True, or just entropy if
        all_info is False.
    """
    returned  = count_segs(corpus, seg1, seg2, sequence_type,
                            type_or_token, stop_check, call_back)
    if stop_check is not None and stop_check():
        return
    seg1_count, seg2_count = returned
    total_count = seg1_count + seg2_count
    if total_count:
        H = -1 * ((seg1_count/total_count) * log2(seg1_count/total_count) \
                + (seg2_count/total_count) * log2(seg2_count/total_count))
    else:
        H = 0.0
    if all_info:
        H = [H, total_count, seg1_count, seg2_count]
    return H


def calc_prod_wordtokens(corpus, envs, sequence_type='transcription',
        type_or_token='most_frequent_type', strict = True, all_info = False, stop_check = None,
                call_back = None):
    """
    Main function for calculating predictability of distribution for
    two segments over specified environments in a corpus, using pronunciation
    variants of words.

    The supported frequency options are as follows: `most_frequent_type`
    selects the most frequent pronunciation variant as the transcription and uses the type
    frequency of the word; `most_frequent_token` does the same thing as
    `most_frequent_type` but uses the token frequency of the word;
    `count_token` treats each pronunciation variant as its own transcription
    and uses the token frequency of each variant; `relative_type` is similar
    to `count_token`, but the frequencies are normalized by the overall
    frequency of the word, yielding a type-like frequency.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : str
        The first segment
    seg2 : str
        The second segment
    envs : list of str
        List of strings that specify environments either using features
        or segments
    sequence_type : str
        Name of the Corpus tier to use for finding environments, defaults
        to 'transcription'
    type_or_token : str {'most_frequent_type', 'most_frequent_token', 'count_token', 'relative_type'}
        Specify whether to use type frequency or token frequency in
        calculating predictability of distribution
    strict : bool
        If true, exceptions will be raised for non-exhausive environments
        and non-unique environments.  If false, only warnings will be
        shown.  Defaults to True.
    all_info : bool
        If true, all the intermediate numbers for calculating predictability
        of distribution will be returned.  If false, only the final entropy
        will be returned.  Defaults to False.
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    dict
        Keys are the environments specified and values are either a list
        of [entropy, frequency of environment, frequency of seg1, frequency
        of seg2] if all_info is True, or just entropy if all_info is False.
    """
    returned = check_envs_wordtokens(corpus, envs,sequence_type, type_or_token, stop_check, call_back)

    if stop_check is not None and stop_check():
        return
    env_matches, miss_envs, overlap_envs = returned
    if miss_envs or overlap_envs:
        if strict:
            raise(ProdError(envs, miss_envs, overlap_envs))

    H_dict = OrderedDict()

    #CALCULATE ENTROPY IN INDIVIDUAL ENVIRONMENTS FIRST
    total_seg1_matches = 0
    total_seg2_matches = 0
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
        seg1_matches = env_matches[env][seg1]
        seg2_matches = env_matches[env][seg2]
        total_seg1_matches += seg1_matches
        total_seg2_matches += seg2_matches

        total_tokens = seg1_matches + seg2_matches
        total_frequency += total_tokens

        if not total_tokens:
            H = 0
        else:
            seg1_prob = seg1_matches/total_tokens
            seg2_prob = seg2_matches/total_tokens
            seg1_H = log2(seg1_prob)*seg1_prob if seg1_prob > 0 else 0
            seg2_H = log2(seg2_prob)*seg2_prob if seg2_prob > 0 else 0
            H = sum([seg1_H, seg2_H])*-1
            if not H:
                H = H+0 #avoid the -0.0 problem
        H_dict[env] = [H, total_tokens, seg1_matches, seg2_matches]

    #CALCULATE WEIGHTED ENTROPY LAST
    weighted_H = 0
    for env in env_matches:
        if total_frequency > 0:
            weighted_H += H_dict[env][0] * (H_dict[env][1] / total_frequency)


    try:
        avg_h = (total_seg1_matches+total_seg2_matches)/total_frequency
    except ZeroDivisionError:
        avg_h = 0.0

    H_dict['AVG'] = (weighted_H, avg_h, total_seg1_matches, total_seg2_matches)

    if not all_info:
        for k,v in H_dict.items():
            H_dict[k] = v[0]
    return H_dict


def calc_prod(corpus, envs, sequence_type='transcription',
        type_or_token='type', strict = True, all_info = False, stop_check = None,
                call_back = None):
    """
    Main function for calculating predictability of distribution for
    two segments over specified environments in a corpus.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : str
        The first segment
    seg2 : str
        The second segment
    envs : list of str
        List of strings that specify environments either using features
        or segments
    sequence_type : str
        Name of the Corpus tier to use for finding environments, defaults
        to 'transcription'
    type_or_token : str
        Specify whether to use type frequency or token frequency in
        calculating predictability of distribution
    strict : bool
        If true, exceptions will be raised for non-exhausive environments
        and non-unique environments.  If false, only warnings will be
        shown.  Defaults to True.
    all_info : bool
        If true, all the intermediate numbers for calculating predictability
        of distribution will be returned.  If false, only the final entropy
        will be returned.  Defaults to False.
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    dict
        Keys are the environments specified and values are either a list
        of [entropy, frequency of environment, frequency of seg1, frequency
        of seg2] if all_info is True, or just entropy if all_info is False.
    """
    seg_list = envs[0].middle
    for e in envs:
        if e.middle != seg_list:
            raise(PCTError("Middle segments of all environments must be the same."))

    returned = check_envs(corpus, envs,sequence_type, type_or_token, stop_check, call_back)

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
        if total_frequency > 0:
            weighted_H += H_dict[env][0] * (H_dict[env][1] / total_frequency)

    try:
        avg_h = sum(total_matches.values())/total_frequency
    except ZeroDivisionError:
        avg_h = 0.0

    H_dict['AVG'] = [weighted_H, avg_h] + [total_matches[x] for x in seg_list]

    if not all_info:
        for k,v in H_dict.items():
            H_dict[k] = v[0]
    return H_dict

