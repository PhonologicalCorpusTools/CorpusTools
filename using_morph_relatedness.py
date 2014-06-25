'''
Created on May 13, 2014

@author: Michael
'''
import morph_relatedness

#Testing mass compare of one word
#morph_relatedness.morph_relatedness_word('iphod', 'string_similarity', 'transcription', 'type', 'dog', 0, output_filename = 'test.txt')
morph_relatedness.morph_relatedness_word('iphod', 'edit_distance', 'transcription', 'type', 'dog', output_filename = 'test4.txt')
#morph_relatedness.morph_relatedness_word('iphod', 'edit_distance', 'spelling', 'type', 'pizza', 0, output_filename = 'test5.txt')

#Testing single pair comparison
#a = morph_relatedness.morph_relatedness_single_pair('iphod', 'string_similarity', 'transcription', 'dog', 'doggie')
#b = morph_relatedness.morph_relatedness_single_pair('iphod', 'string_similarity', 'spelling', 'dog', 'doggie')
#print(a)
#print(b)

#Testing pair comparison
#morph_relatedness.morph_relatedness_pairs('iphod', 'string_similarity', 'spelling', 'type', 'words_2_spell.txt', 'words_2_spell_output.txt', -15)
#morph_relatedness.morph_relatedness_pairs('iphod', 'string_similarity', 'transcription', 'type', 'words_2_trans.txt', 'words_2_trans_output.txt', -15)