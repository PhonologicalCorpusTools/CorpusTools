#fun times with morphological relatedness
import time
import morph_relatedness
import corpustools
import phono_align_ex
from codecs import open

class Freqor(object):

    def calc_freq_of_alt(self, s1, s2, relator_type, string_type, output_filename, threshold = None, phono_align = None, min_pairs_okay = None):     
        print('Gathering Lists of Words with sounds')
        list_s1, list_s2 = self.get_lists(s1, s2, string_type)
        print('Lists complete')
        print('Words with sound 1: ' + str(len(list_s1)))
        print('Words with sound 2: ' + str(len(list_s2)))
        
        start_time = time.time()
        with open('temp_file.txt', mode='w', encoding='utf-8') as outf:
            for word_s1 in list_s1:
                for word_s2 in list_s2:
                    outf.write('{}\t{}\r\n'.format(word_s1, word_s2))
        end_time = time.time()
        print('File creation time: ' + str(end_time-start_time))
        
        related_list = morph_relatedness.morph_relatedness_pairs('iphod', relator_type, string_type, 'temp_file.txt', 'return_data', threshold=threshold, ready_made_corpus = self.corpus)
        
        all_words, words_with_alt = list_s1.union(list_s2), set()
        
        if min_pairs_okay == 0:
            new_related_list = list()
            for w1, w2, score in related_list:
                if len(w1) != len(w2):
                    new_related_list.append( (w1, w2, score) )
                else:
                    count_diff = 0
                    for i in range(len(w1)):
                        if w1[i] != w2[i]:
                            count_diff += 1
                    if count_diff > 1:
                        new_related_list.append( (w1, w2, score) )
            
            related_list = new_related_list
                    
                    
        if phono_align == 1:
            al = phono_align_ex.Aligner(features=self.corpus.specifier.matrix)
            with open(output_filename, mode='w', encoding='utf-8') as outf2:
                for w1, w2, score in related_list:
                    alignment = al.align(w1, w2)
                    #print(al.morpho_related(alignment, s1, s2))
                    if al.morpho_related(alignment, s1, s2):
                        words_with_alt.add(w1)
                        words_with_alt.add(w2)
                        outf2.write('{}\t{}\t{}\r\n'.format(w1, w2, score))
                    
        #Two words above the threshold that in one case have esh and in the other have s
        #divided by the total number of words that have ess or esh
        print('Total number of words:' + str(len(all_words)))
        print('Total words with alternation:' + str(len(words_with_alt)))
        freq_of_alt = len(words_with_alt)/len(all_words)
        #Percent of total words such that
        print('The frequency of alternation is: ' + str(freq_of_alt))

    def get_lists(self, s1, s2, string):
        s1_list = set()
        s2_list = set()
        for w in self.corpus:
            word = getattr(w, string)
            if not isinstance(word, str):
                word = ''.join(seg.symbol for seg in word)
            if s1 in word and s2 in word:
                s1_list.add(word)
                s2_list.add(word)
            elif s1 in word:
                s1_list.add(word)
            elif s2 in word:
                s2_list.add(word)            
            else:
                pass
        return [s1_list, s2_list]

    def __init__(self,corpus_name, size):
        print('Building Corpus')
        start_time = time.time()
        self.factory = corpustools.CorpusFactory()
        self.corpus = self.factory.make_corpus(corpus_name, features='hayes', size=size)
        end_time = time.time()
        print('Corpus Complete')
        print('Corpus creation time: ' + str(end_time-start_time))


if __name__ == '__main__':
    pass
##    relator = Relator('subtlex') #give name of a corpus here, 'iphod' also works
##    relator.relate('children', 'subtlex_children_token_count.txt', string_type='spelling', count_what='token')