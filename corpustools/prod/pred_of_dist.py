from collections import defaultdict
from math import log


def count_segs(corpus, seg1, seg2, type_or_token, tier_name):
    seg1_counts = 0
    seg2_counts = 0

    for word in corpus:
        word = getattr(word, tier_name)
        for seg in word:
            if seg == seg1:
                seg1_counts = seg1_counts+1 if type_or_token == 'type' else seg1_counts+word.abs_freq
            elif seg == seg2:
                seg2_counts = seg2_counts+1 if type_or_token == 'type' else seg2_counts+word.abs_freq

    return seg1_counts, seg2_counts


def check_envs(corpus, seg1, seg2, type_or_token, user_supplied_envs,tier_name):

    count_what = type_or_token
    user_supplied_envs = [formalize_env(env) for env in user_supplied_envs]
    env_matches = {'{}_{}'.format(user_env[0],user_env[1]):{seg1:[0], seg2:[0]} for user_env in user_supplied_envs}

    words_with_missing_envs = defaultdict(list)
    words_with_overlapping_envs = defaultdict(list)

    for word in corpus:
        word.set_string(tier_name) #this makes sure we loop over the right thing
        for pos,seg in enumerate(word):
            if not (seg == seg1 or seg == seg2):
                continue

            if (seg == seg1) and (user_supplied_envs is None):
                if count_what == 'type':
                    value = 1
                elif count_what == 'token':
                    value = word.abs_freq
                env_matches[seg1].append(value)
                continue

            if (seg == seg2) and (user_supplied_envs is None):
                if count_what == 'type':
                    value = 1
                elif count_what == 'token':
                    value = word.abs_freq
                env_matches[seg2].append(value)
                continue


            word_env = word.get_env(pos)
            found_env_match = list()
            for user_env in user_supplied_envs:
                key = '{}_{}'.format(user_env[0],user_env[1])
                if match_to_env(word_env,user_env):
                    if count_what == 'type':
                        value = 1
                    elif count_what == 'token':
                        value = word.abs_freq
                    if seg == seg1:
                        env_matches[key][seg1].append(value)
                        #print(env_matches[key][seg1])
                    else:
                        #print('matched seg {} in word {}'.format(seg1, word))
                        env_matches[key][seg2].append(value)
                    found_env_match.append(user_env)

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

def calc_prod_all_envs(seg1_count, seg2_count):
    total_count = seg1_count + seg2_count
    if total_count:
        H = -1 * ((seg1_count/total_count) * log(seg1_count/total_count) + (seg2_count/total_count) * log(seg2_count/total_count))
    else:
        H = 0.0
    return H


def calc_prod(corpus_name, tier_name, seg1, seg2, env_matches, type_or_token):
    results = []
    H_dict = dict()

    for env in env_matches:
        total_tokens = sum(env_matches[env][seg1]) + sum(env_matches[env][seg2])
        if not total_tokens:
            H_dict[env] = (0,0)
            data = [corpus_name,
                    tier_name,
                    seg1,
                    seg2,
                    env,
                    str(sum(env_matches[env][seg1])),
                    str(sum(env_matches[env][seg2])),
                    str(total_tokens),
                    'N/A',
                    type_or_token]
            results.append(data)
        else:
            seg1_prob = sum(env_matches[env][seg1])/total_tokens
            seg2_prob = sum(env_matches[env][seg2])/total_tokens
            seg1_H = log(seg1_prob,2)*seg1_prob if seg1_prob > 0 else 0
            seg2_H = log(seg2_prob,2)*seg2_prob if seg2_prob > 0 else 0
            H = sum([seg1_H, seg2_H])*-1
            if not H:
                H = H+0
            H_dict[env] = (H, total_tokens)
            data = [corpus_name,
                    tier_name,
                    seg1,
                    seg2,
                    env,
                    str(sum(env_matches[env][seg1])),
                    str(sum(env_matches[env][seg2])),
                    str(total_tokens),
                    str(H),
                    type_or_token]
            results.append(data)

    total_frequency = sum(value[1] for value in H_dict.values())
    for env in env_matches:
        H_dict[env] = H_dict[env][0] * (H_dict[env][1] / total_frequency) if total_frequency>0 else 0
    weighted_H = sum(H_dict[env] for env in H_dict)
    total_seg1_matches = sum([sum(env_matches[env][seg1]) for env in env_matches])
    total_seg2_matches = sum([sum(env_matches[env][seg2]) for env in env_matches])
    data = [corpus_name,
            tier_name,
            seg1,
            seg2,
            'AVG',
            str(total_seg1_matches),
            str(total_seg2_matches),
            str(total_seg1_matches+total_seg2_matches),
            str(weighted_H),
            type_or_token]
    results.append(data)
    return results
