'''
Created on May 13, 2014

@author: Michael
'''
import morph_relatedness
import corpustools

factory = corpustools.CorpusFactory()
corpus = factory.make_corpus('iphod', features='spe', size='all')

#Testing mass compare of one word
morph_relatedness.morph_relatedness_word('iphod', 'string_similarity', 'spelling', 'type', 'cat', -10, 50, output_filename = 'test1.txt', ready_made_corpus = corpus)
morph_relatedness.morph_relatedness_word('iphod', 'string_similarity', 'transcription', 'type', 'cat', -10, 50, output_filename = 'test2.txt', ready_made_corpus = corpus)
morph_relatedness.morph_relatedness_word('iphod', 'edit_distance', 'spelling', 'type', 'cat', 0, 5, output_filename = 'test3.txt', ready_made_corpus = corpus)
morph_relatedness.morph_relatedness_word('iphod', 'edit_distance', 'transcription', 'type', 'cat', 0, 5, output_filename = 'test4.txt', ready_made_corpus = corpus)

#Testing single pair comparison
a = morph_relatedness.morph_relatedness_single_pair('iphod', 'string_similarity', 'spelling', 'dog', 'doggie', ready_made_corpus = corpus)
b = morph_relatedness.morph_relatedness_single_pair('iphod', 'string_similarity', 'transcription', 'dog', 'doggie', ready_made_corpus = corpus)
c = morph_relatedness.morph_relatedness_single_pair('iphod', 'edit_distance', 'spelling', 'dog', 'doggie', ready_made_corpus = corpus)
d = morph_relatedness.morph_relatedness_single_pair('iphod', 'edit_distance', 'transcription', 'dog', 'doggie', ready_made_corpus = corpus)

print(a)
print(b)
print(c)
print(d)

#Testing pair comparison
morph_relatedness.morph_relatedness_pairs('iphod', 'string_similarity', 'spelling', 'type', 'words_2_spell.txt', 'test5.txt', ready_made_corpus = corpus)
morph_relatedness.morph_relatedness_pairs('iphod', 'string_similarity', 'transcription', 'type', 'words_2_spell.txt', 'test6.txt', ready_made_corpus = corpus)

morph_relatedness.morph_relatedness_pairs('iphod', 'edit_distance', 'spelling', 'type', 'words_2_spell.txt', 'test7.txt', ready_made_corpus = corpus)
morph_relatedness.morph_relatedness_pairs('iphod', 'edit_distance', 'transcription', 'type', 'words_2_spell.txt', 'test8.txt', ready_made_corpus = corpus)

morph_relatedness.morph_relatedness_pairs('iphod', 'string_similarity', 'spelling', 'type', 'words_2_spell.txt', 'test9.txt', 0, 50, ready_made_corpus = corpus)
morph_relatedness.morph_relatedness_pairs('iphod', 'string_similarity', 'transcription', 'type', 'words_2_spell.txt', 'test10.txt', 0, 50, ready_made_corpus = corpus)

morph_relatedness.morph_relatedness_pairs('iphod', 'edit_distance', 'spelling', 'type', 'words_2_spell.txt', 'test11.txt', 0, 50, ready_made_corpus = corpus)
morph_relatedness.morph_relatedness_pairs('iphod', 'edit_distance', 'transcription', 'type', 'words_2_spell.txt', 'test12.txt', 0, 50, ready_made_corpus = corpus)
