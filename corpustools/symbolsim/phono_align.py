#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Based on aligner.js (by Michael Becker and Blake Allen),
## which in turn was based on Peter Kleiweg's Levenshtein Demo.

from collections import defaultdict
from codecs import open

class Aligner(object):

    def __init__(self, features_tf=True, ins_penalty=1, del_penalty=1,
                 sub_penalty=1, tolerance=0, features=None,
                 underspec_cost=0.25,
                 ins_del_basis='empty'): # other option is 'average'
        self.features_tf = features_tf
        self.ins_penalty = ins_penalty
        self.del_penalty = del_penalty
        self.sub_penalty = sub_penalty
        self.tolerance = tolerance
        self.features = features
        self.underspec_cost = underspec_cost # should be set to 1.0 to disable underspecification
        self.ins_del_basis = ins_del_basis

        if features_tf:
            if self.ins_del_basis == 'empty':
                try:
                    self.silence_features = self.features['empty']
                except (TypeError, KeyError):
                    feature_names = self.features.features
                    self.silence_features = {}
                    for feature in feature_names:
                        self.silence_features[feature] = '0'
            elif self.ins_del_basis == 'average':
                total = 0
                for segment1 in self.features:
                    for segment2 in self.features:
                        if segment1 != segment2:
                            total += self.compare_segments(segment1, segment2, self.underspec_cost)
                self.ins_del_difference = total / (len(self.features)^2 - len(self.features))

    def align(self, seq1=None, seq2=None):
        similarity_matrix = self.make_similarity_matrix(seq1, seq2)
        alignment = self.generate_alignment(seq1, seq2, similarity_matrix)
        return alignment



    def make_similarity_matrix(self, seq1=None, seq2=None):

        d = []

        seq1 = list(seq1)
        seq2 = list(seq2)

        def compare(x, y):
            return x - y <= self.tolerance

        initial_vals = {'aboveleft': 0,
                        'above': 0,
                        'left': 0,
                        'trace': 0,
                        'f': None}

        d = [[initial_vals.copy() for y in seq2+[' ']] for x in seq1+[' ']]
        d[0][0]['f'] = 0

        for x in range(1, len(seq1)+1):
            d[x][0]['f'] = d[x-1][0]['f'] + self.compare_segments(seq1[x-1], 'empty', self.underspec_cost)
            d[x][0]['left'] = 1

        for y in range(1, len(seq2)+1):
            d[0][y]['f'] = d[0][y-1]['f'] + self.compare_segments('empty', seq2[y-1], self.underspec_cost)
            d[0][y]['above'] = 1

        for x in range(1, len(seq1)+1):
            for y in range(1, len(seq2)+1):
                aboveleft = (d[x - 1][y - 1]['f'] + self.compare_segments(seq1[x-1], seq2[y-1], self.underspec_cost))
                left = d[x - 1][y]['f'] + self.compare_segments(seq1[x-1], 'empty', self.underspec_cost)
                above = d[x][y - 1]['f'] + self.compare_segments('empty', seq2[y-1], self.underspec_cost)

                if compare(aboveleft,above) and compare(aboveleft,left):
                    d[x][y]['f'] = aboveleft
                    d[x][y]['aboveleft'] = 1

                if compare(above,aboveleft) and compare(above,left):
                    d[x][y]['f'] = above
                    d[x][y]['above'] = 1

                if compare(left,aboveleft) and compare(left,above):
                    d[x][y]['f'] = left
                    d[x][y]['left'] = 1

                d[x][y]['f'] = min(aboveleft, above, left)

        return d



    def compare_segments(self, segment1, segment2, underspec_cost=.25):

        def check_feature_difference(val1, val2, underspec_cost):
            if val1 == val2:
                return 0
            elif val1 == '0' or val2 == '0':
                return underspec_cost
            else:
                return 1

        if type(segment1) is str:
            segment1symbol = segment1
        else:
            segment1symbol = segment1.symbol
        if type(segment2) is str:
            segment2symbol = segment2
        else:
            segment2symbol = segment2.symbol
        if self.features_tf:
            if segment1 == 'empty':
                fs2 = self.features[segment2symbol]
                if self.ins_del_basis == 'empty':
                    distance = (sum(check_feature_difference('0',
                            sign, underspec_cost) for sign in fs2.values()))
                elif self.ins_del_basis == 'average':
                    distance = ins_del_difference
                return distance * self.ins_penalty

            elif segment2 == 'empty':
                fs1 = self.features[segment1symbol]
                if self.ins_del_basis == 'empty':
                    distance = (sum(check_feature_difference(sign,
                        '0', underspec_cost) for sign in fs1.values()))
                elif self.ins_del_basis == 'average':
                    distance = ins_del_difference
                return distance * self.del_penalty
            else:
                fs1 = self.features[segment1symbol]
                fs2 = self.features[segment2symbol]
                return (sum(check_feature_difference(fs1[k], fs2[k], underspec_cost) for k in fs1.keys()) * self.sub_penalty)
        else:
            if segment1 == 'empty':
                return self.ins_penalty
            elif segment2 == 'empty':
                return self.del_penalty
            else:
                return int(segment1!=segment2) * self.sub_penalty


    def generate_alignment(self, seq1, seq2, d):
        alignments = []
        x = len(seq1)
        y = len(seq2)
        current_alignment = []

        while x > 0 or y > 0:
            if d[x][y]['aboveleft']:
                current_element = {'elem1': seq1[x-1], 'elem2': seq2[y-1], 'dir': 'aboveleft'}
                current_alignment = [current_element] + current_alignment
                x -= 1
                y -= 1
            elif d[x][y]['above']:
                current_element = {'elem1': None, 'elem2': seq2[y-1], 'dir': 'above'}
                current_alignment = [current_element] + current_alignment
                y -= 1
            elif d[x][y]['left']:
                current_element = {'elem1': seq1[x-1], 'elem2': None, 'dir': 'left'}
                current_alignment = [current_element] + current_alignment
                x -= 1

        return current_alignment

    def morpho_related(self, alignment, s1, s2):
        core = []
        adding = 0
        for chunk in alignment:
            if not adding:
                if chunk['elem1'] != None and chunk['elem2'] != None:
                    adding = 1
                    core.append(chunk)
            elif adding:
                if chunk['elem1'] == None or chunk['elem2'] == None:
                    break
                else:
                    core.append(chunk)

        def acceptable_core(cr, s1, s2):
            found_alternation = False
            def acceptable_chunk(chunk, s1, s2):
                if chunk['elem1'] == chunk['elem2']:
                    return 'identical'
                elif chunk['elem1'] == s1 and chunk['elem2'] == s2:
                    return 'alternation'
                elif chunk['elem1'] == s2 and chunk['elem2'] == s1:
                    return 'alternation'
                else:
                    return False
            chunk_statuses = [acceptable_chunk(chunk, s1, s2) for chunk in cr]
            if False not in chunk_statuses:
                if 'alternation' in chunk_statuses:
                    return True
            return False

        return acceptable_core(core, s1, s2)



def make_feature_dict(feature_file):
    instring = feature_file.read().split('\n')
    colnames = instring[0].split('\t')
    segments = [line.split('\t') for line in instring[1:]][:-1]
    feature_dict = {}
    for segment in segments:
        values_dict = {}
        for i,feature_name in enumerate(colnames[1:]):
            values_dict[feature_name] = segment[i+1]
        feature_dict[segment[0]] = values_dict

    return feature_dict
