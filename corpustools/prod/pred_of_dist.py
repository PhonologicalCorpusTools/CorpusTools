from collections import defaultdict, OrderedDict
from math import log2

from warnings import warn

from corpustools.corpus.classes import Environment as WordEnvironment

class ExhaustivityError(Exception):
    pass

class UniquenessError(Exception):
    pass

class ExhaustivityWarning(Warning):
    pass

class UniquenessWarning(Warning):
    pass

class Environment(object):
    def __init__(self, corpus, env):

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
            self.lhs_string  = ''
            self.lhs = list()
        elif lhs.startswith('['):
            self.lhs_string = lhs
            lhs = lhs.lstrip('[')
            lhs = lhs.rstrip(']')
            #lhs = {feature[1:]:feature[0] for feature in lhs.split(',')}
            lhs = lhs.split(',')
            self.lhs = corpus.features_to_segments(lhs)
        #else it's a segment, just leave it as the string it already is
        else:
            self.lhs_string = lhs
            self.lhs = [lhs]

        if not rhs:
            self.rhs_string  = ''
            self.rhs = list()
        elif rhs.startswith('['):
            self.rhs_string = rhs
            rhs = rhs.lstrip('[')
            rhs = rhs.rstrip(']')
            #rhs = {feature[1:]:feature[0] for feature in rhs.split(',')}
            rhs = rhs.split(',')
            self.rhs = corpus.features_to_segments(rhs)
        #else it's a segment, just leave it as the string it already is
        else:
            self.rhs_string = rhs
            self.rhs = [rhs]

    def __str__(self):
        return '_'.join([self.lhs_string,self.rhs_string])

    def __eq__(self, other):
        if not hasattr(other,'lhs'):
            return False
        if not hasattr(other,'rhs'):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def __hash__(self):
        return hash((self.rhs_string, self.lhs_string))

    def __contains__(self, item):
        if not isinstance(item, WordEnvironment):
            return False
        if self.rhs:
            if item.rhs not in self.rhs:
                return False
        if self.lhs:
            if item.lhs not in self.lhs:
                return False
        return True


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

    envs = [Environment(corpus, env) for env in envs]
    env_matches = {env:{seg1:[0], seg2:[0]} for env in envs}

    missing_envs = set()
    overlapping_envs = defaultdict(set)

    for word in corpus:
        for pos,seg in enumerate(getattr(word, tier_name)):
            if not (seg == seg1 or seg == seg2):
                continue

            word_env = word.get_env(pos, tier_name)
            found_env_match = list()
            for env in envs:
                if word_env in env:
                    if type_or_token == 'type':
                        value = 1
                    elif type_or_token == 'token':
                        value = word.frequency
                    env_matches[env][seg].append(value)
                    found_env_match.append(env)

            if not found_env_match:
                #found and environemnts with segs the user wants, but in
                #an environement that was not supplied. Alert the user
                #about this later
                missing_envs.update([str(word_env)])

            elif len(found_env_match) > 1:
                #the user supplied environmnets that overlap, e.g. they want
                #_[-voice] and also _k, but we shouldn't count this twice
                #alert the user about this later
                overlapping_envs[tuple(str(env) for env in found_env_match)].update([str(word_env)])

    return env_matches, missing_envs, overlapping_envs

def calc_prod_all_envs(corpus, seg1, seg2, tier_name = 'transcription', type_or_token = 'type', all_info = False):
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
    tier_name : string
        Name of the Corpus tier to use for finding environments, defaults
        to 'transcription'
    type_or_token : string
        Specify whether to use type frequency or token frequency in
        calculating predictability of distribution
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
    """
    Main function for calculating predictability of distribution for
    two segments over specified environments in a corpus.

    Parameters
    ----------
    corpus : Corpus
        The Corpus object to use
    seg1 : string
        The first segment
    seg2 : string
        The second segment
    envs : list of strings
        List of strings that specify environments either using features
        or segments
    tier_name : string
        Name of the Corpus tier to use for finding environments, defaults
        to 'transcription'
    type_or_token : string
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

    Returns
    -------
    dictionary
        Keys are the environments specified and values are either a list
        of [entropy, frequency of environment, frequency of seg1, frequency
        of seg2] if all_info is True, or just entropy if all_info is False.
    """
    env_matches, miss_envs, overlap_envs = check_envs(corpus, seg1, seg2, envs,tier_name, type_or_token)
    if miss_envs:
        error_string = 'The environments {} for {} were not applicable to the following environments: {}'.format(
                    ' ,'.join(str(env) for env in envs),
                    ' and '.join([seg1, seg2]),
                    ' ,'.join(str(w) for w in miss_envs))
        if strict:
            raise(ExhaustivityError(error_string))
        else:
            warn(error_string, ExhaustivityWarning)

    if overlap_envs:
        error_string = 'The following environments for {} overlapped:\n'.format(' and '.join([seg1, seg2]))
        for k,v in overlap_envs.items():
            error_string +='{}: {}\n'.format(
                    ' ,'.join(str(env) for env in k),
                    ' ,'.join(str(env) for env in v))
        if strict:
            raise(UniquenessError(error_string))
        else:
            warn(error_string, UniquenessWarning)

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

