from collections import defaultdict, OrderedDict
from math import log2

from warnings import warn

class ExhaustivityError(Exception):
    pass

class UniquenessWarning(Warning):
    pass

class ExhaustivityError(Exception):
    pass

class UniquenessWarning(Warning):
    pass

def count_segs(corpus, seg1, seg2, tier_name, type_or_token):
    seg1_counts = 0
    seg2_counts = 0

    for word in corpus:
        tier = getattr(word, tier_name)
        for seg in tier:
            if seg == seg1:
                seg1_counts = seg1_counts+1 if type_or_token == 'type' else seg1_counts+word.frequency
            elif seg == seg2:
                seg2_counts = seg2_counts+1 if type_or_token == 'type' else seg2_counts+word.frequency

    return seg1_counts, seg2_counts


def check_envs(corpus, seg1, seg2, envs, tier_name, type_or_token):

    envs = [formalize_env(env) for env in envs]
    env_matches = {'{}_{}'.format(env[0],env[1]):{seg1:[0], seg2:[0]} for env in envs}

    words_with_missing_envs = defaultdict(list)
    words_with_overlapping_envs = defaultdict(list)

    for word in corpus:
        for pos,seg in enumerate(getattr(word, tier_name)):
            if not (seg == seg1 or seg == seg2):
                continue

            #if (seg == seg1) and (not env_list):
                #if type_or_token == 'type':
                    #value = 1
                #elif type_or_token == 'token':
                    #value = word.frequency
                #env_matches[seg1].append(value)
                #continue

            #if (seg == seg2) and (not env_list):
                #if type_or_token == 'type':
                    #value = 1
                #elif type_or_token == 'token':
                    #value = word.frequency
                #env_matches[seg2].append(value)
                #continue


            word_env = word.get_env(pos, tier_name)
            found_env_match = list()
            for env in envs:
                key = '{}_{}'.format(env[0],env[1])
                if match_to_env(word_env,env):
                    if type_or_token == 'type':
                        value = 1
                    elif type_or_token == 'token':
                        value = word.frequency
                    if seg == seg1:
                        env_matches[key][seg1].append(value)
                    else:
                        env_matches[key][seg2].append(value)
                    found_env_match.append(env)

            if not found_env_match:
                #found and environemnts with segs the user wants, but in
                #an environement that was not supplied. Alert the user
                #about this later
                words_with_missing_envs[word.spelling].append(str(word_env))

            elif len(found_env_match) > 1:
                #the user supplied environmnets that overlap, e.g. they want
                #_[-voice] and also _k, but we shouldn't count this twice
                #alert the user about this later
                words_with_overlapping_envs[word.spelling].extend([str(env) for env in found_env_match])

    return env_matches, words_with_missing_envs, words_with_overlapping_envs

def match_to_env(word_env,user_env):

    lhs,rhs = user_env
    l_match = False
    r_match = False
    if not lhs:
        l_match = True
        #empty side is a wildcard, so an automatic matches
    elif type(lhs)==str:
        if lhs == word_env.lhs.symbol:
            l_match = True
    else: #it's a feature list
        for feature in lhs:
            try:
                match = feature[0] == word_env.lhs.features[feature[1:]]
            except KeyError:
                break
            if not match:
                break
        else:
            l_match = True
        #if all([word_env.lhs.features[feature]==lhs[feature] for feature in lhs]):
         #   l_match = True

    if not rhs:
        r_match = True
        #empty sides is a wildcard, so an automatic matches
    elif type(rhs)==str:
        if rhs == word_env.rhs.symbol:
            r_match = True
    else: #it's a feature list
        for feature in rhs:
            try:
                match = feature[0] == word_env.rhs.features[feature[1:]]
            except KeyError:
                break #occurs with word bounarires and other non-segmental things
            if not match:
                break
        else:
            r_match = True
        #if all([word_env.rhs.features[feature]==rhs[feature] for feature in rhs]):
         #   r_match = True

    if l_match and r_match:
        #print('YEAH match for word {} on tier {}'.format(word.spelling, word_env))
        return True
    else:
        return False

def formalize_env(env):

    #there's a problem where some feature names have underscores in them
    #so doing lhs,rhs=env.split('_') causes unpacking problems
    #this in an awakward work-around that checks to see if either side of
    #the environment is a list of features, by looking for brackets, then
    #splits by brackets if necessary. However, I can't split out any
    #starting brackets [ because I also use those for identifying lists
    #at a later point
    #otherwise, if its just segment envrionments, split by underscore
    if ']_[' in env:
        #both sides are lists
        lhs, rhs = env.split(']_')
    elif '_[' in env:
        #only the right hand side is a list of a features
        lhs, rhs = env.split('_', maxsplit=1)
    elif ']_' in env:
        #only the left hand side is a list of features
        lhs, rhs = env.split(']_')
    else: #both sides are segments
        lhs, rhs = env.split('_')

    if not lhs:
        pass
    elif lhs.startswith('['):
        lhs = lhs.lstrip('[')
        lhs = lhs.rstrip(']')
        #lhs = {feature[1:]:feature[0] for feature in lhs.split(',')}
        lhs = lhs.split(',')
    #else it's a segment, just leave it as the string it already is

    if not rhs:
        pass
    elif rhs.startswith('['):
        rhs = rhs.lstrip('[')
        rhs = rhs.rstrip(']')
        #rhs = {feature[1:]:feature[0] for feature in rhs.split(',')}
        rhs = rhs.split(',')
    #else it's a segment, just leave it as the string it already is

    #env = corpustools.Environment(lhs, rhs)
    return (lhs,rhs)

def calc_prod_all_envs(corpus, seg1, seg2, tier_name = 'transcription', type_or_token = 'type', all_info = False):
    seg1_count, seg2_count = count_segs(corpus, seg1, seg2, tier_name, type_or_token)
    total_count = seg1_count + seg2_count
    if total_count:
        H = -1 * ((seg1_count/total_count) * log2(seg1_count/total_count) + (seg2_count/total_count) * log2(seg2_count/total_count))
    else:
        H = 0.0
    if all_info:
        H = [H, total_count, seg1_count, seg2_count]
    return H


def calc_prod(corpus, seg1, seg2, envs, tier_name='transcription', type_or_token='type', strict = True, all_info = False):
    env_matches, miss_envs, overlap_envs = check_envs(corpus, seg1, seg2, envs,tier_name, type_or_token)
    if miss_envs:
        error_string = 'The environments {} for {} were not applicable to the following words: {}'.format(
                    ' ,'.join(str(env) for env in envs),
                    ' and '.join([seg1, seg2]),
                    ' ,'.join(str(w) for w in miss_envs.keys()))
        if strict:
            raise(ExhaustivityError(error_string))
        else:
            warn(ExhaustivityWarning(error_string))

    if overlap_envs:
        error_string = 'The environments {} for {} were overlapping in the following words: {}'.format(
                    ' ,'.join(str(env) for env in envs),
                    ' and '.join([seg1, seg2]),
                    ' ,'.join(str(w) for w in miss_envs.keys()))
        if strict:
            raise(UniquenessError(error_string))
        else:
            warn(UniquenessWarning(error_string))

    H_dict = OrderedDict()

    #CALCULATE ENTROPY IN INDIVIDUAL ENVIRONMENTS FIRST
    total_seg1_matches = 0
    total_seg2_matches = 0
    total_frequency = 0
    for env in env_matches:
        seg1_matches = sum(env_matches[env][seg1])
        seg2_matches = sum(env_matches[env][seg2])
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
        weighted_H += H_dict[env][0] * (H_dict[env][1] / total_frequency) if total_frequency>0 else 0


    try:
        avg_h = (total_seg1_matches+total_seg2_matches)/total_frequency
    except ZeroDivisionError:
        avg_h = 0.0

    H_dict['AVG'] = (weighted_H, avg_h, total_seg1_matches, total_seg2_matches)

    if not all_info:
        for k,v in H_dict.items():
            H_dict[k] = v[0]
    return H_dict

