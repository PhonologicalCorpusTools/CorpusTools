'''
Created on May 13, 2014

@author: Michael
'''
import morph_relatedness

#morph_relatedness.morph_relatedness_word('iphod', 'string_similarity', 'spelling', 'cry', 0)
morph_relatedness.morph_relatedness_pairs('iphod', 'string_similarity', 'spelling', 'words_2_spell.txt', 'words_2_output.txt', -15)