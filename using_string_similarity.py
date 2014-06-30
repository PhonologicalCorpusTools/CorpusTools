'''
Created on May 13, 2014

@author: Michael
'''
import string_similarity
import corpustools

print('Building Corpus')
factory = corpustools.CorpusFactory()
corpus = factory.make_corpus('iphod', features='spe', size='all')
print('Corpus Complete')

string_similarity.string_similarity_word('iphod', 'phono_edit_distance', 'transcription', 'type', 'cat', 0, 5, output_filename = 'test10.txt', ready_made_corpus = corpus)

"""
#Testing mass compare of one word
string_similarity.string_similarity_word('iphod', 'khorsi', 'spelling', 'type', 'cat', -10, 50, output_filename = 'test1.txt', ready_made_corpus = corpus)
string_similarity.string_similarity_word('iphod', 'khorsi', 'transcription', 'type', 'cat', -10, 50, output_filename = 'test2.txt', ready_made_corpus = corpus)
string_similarity.string_similarity_word('iphod', 'edit_distance', 'spelling', 'type', 'cat', 0, 5, output_filename = 'test3.txt', ready_made_corpus = corpus)
string_similarity.string_similarity_word('iphod', 'edit_distance', 'transcription', 'type', 'cat', 0, 5, output_filename = 'test4.txt', ready_made_corpus = corpus)

#Testing single pair comparison
a = string_similarity.string_similarity_single_pair('iphod', 'khorsi', 'spelling', 'dog', 'doggie', ready_made_corpus = corpus)
b = string_similarity.string_similarity_single_pair('iphod', 'khorsi', 'transcription', 'dog', 'doggie', ready_made_corpus = corpus)
c = string_similarity.string_similarity_single_pair('iphod', 'edit_distance', 'spelling', 'dog', 'doggie', ready_made_corpus = corpus)
d = string_similarity.string_similarity_single_pair('iphod', 'edit_distance', 'transcription', 'dog', 'doggie', ready_made_corpus = corpus)

print(a)
print(b)
print(c)
print(d)

#Testing pair comparison
string_similarity.string_similarity_pairs('iphod', 'khorsi', 'spelling', 'type', 'words_2_spell.txt', 'test5.txt', ready_made_corpus = corpus)
string_similarity.string_similarity_pairs('iphod', 'khorsi', 'transcription', 'type', 'words_2_spell.txt', 'test6.txt', ready_made_corpus = corpus)

string_similarity.string_similarity_pairs('iphod', 'edit_distance', 'spelling', 'type', 'words_2_spell.txt', 'test7.txt', ready_made_corpus = corpus)
string_similarity.string_similarity_pairs('iphod', 'edit_distance', 'transcription', 'type', 'words_2_spell.txt', 'test8.txt', ready_made_corpus = corpus)

string_similarity.string_similarity_pairs('iphod', 'khorsi', 'spelling', 'type', 'words_2_spell.txt', 'test9.txt', 0, 50, ready_made_corpus = corpus)
string_similarity.string_similarity_pairs('iphod', 'khorsi', 'transcription', 'type', 'words_2_spell.txt', 'test10.txt', 0, 50, ready_made_corpus = corpus)

string_similarity.string_similarity_pairs('iphod', 'edit_distance', 'spelling', 'type', 'words_2_spell.txt', 'test11.txt', 0, 50, ready_made_corpus = corpus)
string_similarity.string_similarity_pairs('iphod', 'edit_distance', 'transcription', 'type', 'words_2_spell.txt', 'test12.txt', 0, 50, ready_made_corpus = corpus)
"""
