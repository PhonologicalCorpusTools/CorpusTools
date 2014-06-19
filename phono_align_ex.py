#!/usr/bin/env python
# -*- coding: utf-8 -*-


## Based on aligner.js (by Michael Becker and Blake Allen),
## which in turn was based on Peter Kleiweg's Levenshtein Demo.

import random
from collections import defaultdict
from codecs import open

class Aligner(object):

    def __init__(self, features_tf=True, ins_penalty=1, del_penalty=1, 
                 sub_penalty=1, tolerance=0, features=None):
        self.features_tf = features_tf
        self.ins_penalty = ins_penalty
        self.del_penalty = del_penalty
        self.sub_penalty = sub_penalty
        self.tolerance = tolerance
        self.features = features

        try:
            self.silence_features = self.features['empty']
        except (TypeError, KeyError):
            rand_segment = random.choice(list(features.keys()))
            self.silence_features = {}
            for feature in self.features[rand_segment]:
                self.silence_features[feature.name] = '0'

    def align(self, seq1=None, seq2=None):
        similarity_matrix = self.make_similarity_matrix(seq1, seq2)
        alignment = self.generate_alignment(seq1, seq2, similarity_matrix)
        return alignment



    def make_similarity_matrix(self, seq1=None, seq2=None):
        # print(seq1)
        # print(seq2)

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
            d[x][0]['f'] = d[x-1][0]['f'] + self.compare_segments(seq1[x-1], 'empty')
            d[x][0]['left'] = 1

        for y in range(1, len(seq2)+1):
            d[0][y]['f'] = d[0][y-1]['f'] + self.compare_segments('empty', seq2[y-1])
            d[0][y]['above'] = 1

        for x in range(1, len(seq1)+1):
            for y in range(1, len(seq2)+1):
                aboveleft = (d[x - 1][y - 1]['f'] + self.compare_segments(seq1[x-1], seq2[y-1]))
                left = d[x - 1][y]['f'] + self.compare_segments(seq1[x-1], 'empty')
                above = d[x][y - 1]['f'] + self.compare_segments('empty', seq2[y-1])

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
        # print(self.features['t'])

        def check_feature_difference(val1, val2):  
            if val1 == val2:
                return 0
            elif val1 == '0' or val2 == '0':
                return underspec_cost
            else:
                return 1

        # print(segment1)
        # print(segment2)
        if self.features_tf:
            if segment1 == 'empty':
                fs2 = self.features[segment2.symbol]
                return (sum(check_feature_difference('0', 
                            f.sign) for f in fs2) * self.ins_penalty)    # or should this be addition?
            elif segment2 == 'empty':
                fs1 = self.features[segment1.symbol]
                # print(fs1)
                # print(fs1[0])
                return (sum(check_feature_difference(f.sign, 
                        '0') for f in fs1) * 
                        self.del_penalty)    # or should this be addition?
            else:
                fs1 = self.features[segment1.symbol]
                fs2 = self.features[segment2.symbol]
                # print(segment1)
                # print(fs1)
                # print(segment2)
                # print(fs2)
                # for i in range(len(fs1)):
                #     print(fs1[i])
                #     print(fs2[i])
                # print()
                return (sum(check_feature_difference(fs1[i].sign, fs2[i].sign)
                            for i in range(len(fs1))) * self.sub_penalty)    # or should this be addition?
        else:
            if segment1 == 'empty':
                return self.ins_penalty * underspec_cost
            elif segment2 == 'empty':
                return self.del_penalty * underspec_cost
            else:
                return int(segment1!=segment2) * self.sub_penalty   # or should this be addition (with, in this case, a boolean condition)?


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

        def acceptable_core(cr, s1, s2): # refactor this function.
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
            # print(chunk_statuses)
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


if __name__ == '__main__':
    
    import corpustools
    factory = corpustools.CorpusFactory()
    corpus = factory.make_corpus('IPhOD', features='hayes', size=20)
    alr = Aligner(features=corpus.specifier.matrix)
    amt = alr.align('kənfɛs', 'kənfɛʃən')
    alr.morpho_related(amt, 's', 'ʃ')