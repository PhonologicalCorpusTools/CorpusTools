#fun times with morphological relatedness
import math
import pprint
import corpustools
import os
import collections
import re
from codecs import open

class Relator(object):

    def lcs(self, w1, w2):
        #lcs = longest common sequence
        #Ensure we are working with the longer of the two words
        #print('in lcs, w1={}({}) and w1={}({})'.format(w1, type(w1), w2, type(w2)))
        if len(w1) >= len(w2):
            x1 = w1
            x2 = w2
        else:
            x1 = w2
            x2 = w1
        #Compare strings
        stringMatches = []
        for i in range(len(x1)):
            i = i + 1
            #Get all possible substrings of word x1
            substrings = self.substring(x2, i)
            #Compare all substrings to see which is the longest that matches a substring in word x2
            if isinstance(x1, str):
                for j in substrings:
                    if x1.find(j) != -1:
                        stringMatches.append(j)
            else:
                for j in substrings:
                    if self.sublist(j,x1):
                        stringMatches.append(j)

        #As of now, stringMatches is a list of all shared sequences (matched substrings) from 1 letter to the longest possible

        #Remove the longest common sequence if it exists and return the leftovers
        if len(stringMatches)!=0:
            large = max(stringMatches, key=len)
        else:
            large = ''
        try:
            leftOver = x1.replace(large, '')
            leftOver2 = x2.replace(large, '')
            leftOver = leftOver + leftOver2
        except AttributeError:
            if large:
                leftOver = list()
                slices = self.sublist(large,x1)
                leftOver.extend(x1[:slices[0]])
                leftOver.extend(x1[slices[1]:])
                slices = self.sublist(large,x2)
                leftOver.extend(x2[:slices[0]])
                leftOver.extend(x2[slices[1]:])
                #leftOver = ''.join(seg.symbol for seg in x1).replace(large, '')
                #leftOver2 = ''.join(seg.symbol for seg in x2).replace(large, '')
            else:
                leftOver = [seg for seg in x1]
                leftOver.extend([seg for seg in x2])
        #print('stringMatches={}\nlarge={}\nleftover1={}({})'.format(stringMatches, large, leftOver, type(leftOver)))

        return large, leftOver

    def sublist(self,small, big):
        for i in range(len(big)-len(small)+1):
            for j in range(len(small)):
                if big[i+j] != small[j]:
                    break
            else:
                return i, i+len(small)
        return False

    def substring(self, w, l):
        #return all substrings of a word w of length l from 1 letter to the entire word
        substrings = []
        for i in range(len(w)):
            substrings.append(w[i:(i+l)])
        substrings = substrings[0:(len(w)-l+1)]
        return substrings

    def morpho_rel(self, w1, w2, freq_base):
        #Get the longest common sequence and the left overs
        longComSeq = self.lcs(w1, w2)
        longest, left_over = longComSeq
        if isinstance(longest, str) and isinstance(left_over, str):
            longest = re.sub("[\W\d]", "", longest.strip())
            left_over = re.sub("[\W\d]", "", left_over.strip())
        else:
            pass
        total_freq = sum(value for value in freq_base.values())

        #Calculate sums
        if isinstance(w1, str):
            sum1 = sum(math.log(1/(freq_base[letter]/total_freq)) for letter in longest)
            sum2 = sum(math.log(1/(freq_base[letter]/total_freq)) for letter in left_over)
        else:
            sum1 = sum(math.log(1/(freq_base[seg.symbol]/total_freq)) for seg in longest)
            sum2 = sum(math.log(1/(freq_base[seg.symbol]/total_freq)) for seg in left_over)

        return sum1-sum2

    def freq_word_list(self, string, count_what = 'type'):
        self.count_what = count_what
        freq_base = collections.defaultdict(int)
        words = list()
        for word in self.corpus:

            if self.count_what == 'token':
                if self.corpus.name.lower() == 'iphod':
                    frequency = word.abs_freq
                elif self.corpus.name.lower() == 'subtlex':
                    frequency = word.freq_per_mil
                else: #it's a custom corpus
                    frequency = word.frequency

            word = getattr(word, string)
            for letter in word:
                try: #see if it's a str()
                    if self.count_what == 'type':
                        freq_base[letter] += 1
                    elif self.count_what == 'token':
                        freq_base[letter] += frequency
                except TypeError: #it's a Segment(), get a string representation
                    if self.count_what == 'type':
                        freq_base[letter.symbol] += 1
                    elif self.count_what == 'token':
                        freq_base[letter.symbol] += frequency
        return freq_base

    def compare_word(self,w, string):

        #Compare word w with all words in a self.corpus for their morphological relatedness
        freq_base = self.freq_word_list(string)
        #Initiate a list which will hold relatedness values
        relate = list()
        #Calculate relatedness for each word in a corpus compared to our target word
        for word in self.corpus:
            word = getattr(word, string)
            if word is None:
                continue
            #elif not isinstance(word, str): #it's a Segment
            #    word = ''.join([seg.symbol for seg in word])

            relatedness = [self.morpho_rel(w, word, freq_base)]
            relate.append( (relatedness, word) )


        #Sort the lists by most morphologically related
        relate.sort(key=lambda t:t[0])
        relate.reverse()
        return relate


    def word_corpus_compare(self, w, file_name, string='spelling'):
        #Create a file with relatedness values for a target word
        w = getattr(w, string)
        #if not isinstance(w, str):
        #    w = ''.join([letter.symbol for letter in w])
        comp = self.compare_word(w, string)

        if not file_name.endswith('.txt'):
            file_name += '.txt'
        with open(file_name, mode='w', encoding='utf-8') as outf:
            if not isinstance(w, str):
                w = ''.join([seg.symbol for seg in w])
            print('Morphological relatedness to the word: {}\r\n\r\n'.format(w), file=outf)
            for score,word in comp:
                if not isinstance(word, str):
                    word = ''.join([seg.symbol for seg in word])
                print('{} {}\r\n'.format(score,word), file=outf)


    def relate(self, query, output_file_name, string_type='spelling', count_what='type'):
        self.count_what = count_what
        word = self.corpus.find(query)
        self.word_corpus_compare(word,
                            os.path.join(os.getcwd(),output_file_name), string_type)

    def __init__(self,corpus_name=None,ready_made_corpus=None):
        if ready_made_corpus is not None:
            self.corpus = ready_made_corpus
            return

        self.factory = corpustools.CorpusFactory()
        self.corpus = self.factory.make_corpus(corpus_name, features='spe', size='all')


if __name__ == '__main__':
    pass

##    relator = Relator('subtlex') #give name of a corpus here, 'iphod' also works
##    relator.relate('children', 'subtlex_children_token_count.txt', string_type='spelling', count_what='token')
