import math
import collections
import re
import time
from codecs import open

import corpustools

class Relator(object):
    """Initializes the string similarity relator based off the algorithm
    of morphological relatedness found in Khorsi (2012)

    Parameters
    ----------
    object: list
        contains parameters needed for the corpus which will be used in relating elements, some examples could be a corpus name or an already created corpus

    Returns
    -------
    Returns a relator type which can be used to call methods
    """

    def lcs(self, x1, x2):
        """Returns the longest common sequence of two strings or lists of transcription characters and the remainder elements not in the longest common sequence

        Parameters
        ----------
        x1: list
            List of strings
        x2: list
            List of strings

        Returns
        -------
        list
            the list of the longest common sequence of two lists
        list
            the list of remaining elements of both x1 and x2 that are not in the longest common sequence
        """
        if len(x1) >= len(x2):
            longer = x1
            shorter = w2
        else:
            longer = w2
            shorter = w1

        stringMatches = []
        largestMatch = None
        for i in range(len(shorter),0,-1):
            #Get all possible substrings of word x1
            shorter_strings = self.substring(shorter, i)
            longer_strings = self.substring(longer, i)

            s = shorter_strings & longer_strings

            if len(s):
                largestMatch = sorted(list(s))[0]
                break
        else:
            return [], longer+shorter

        lcs = s.split('.') #back to list
        leftover = []
        for i in range(longer):
            begin = i
            end = i+len(lcs)
            if longer[begin:end] == lcs:
                break
        leftover.extend(longer[:begin])
        leftover.extend(longer[end:])
        for i in range(shorter):
            begin = i
            end = i+len(lcs)
            if shorter[begin:end] == lcs:
                break
        leftover.extend(shorter[:begin])
        leftover.extend(shorter[end:])
        return lcs,leftover

    def sublist(self,small, big):
        """Scott wrote this

        Parameters
        ----------


        Returns
        -------


        """
        for i in range(len(big)-len(small)+1):
            for j in range(len(small)):
                if big[i+j] != small[j]:
                    break
            else:
                return i, i+len(small)
        return False

    def substring(self, w, l):
        """Returns all substrings of a word w of length l

        Parameters
        ----------
        w: string
            a string representing a word (e.g. 'pressure')
        l: int
            a integer of a certain length

        Returns
        -------
        list
            A list of strings where each string is a properly ordered subset of w (i.e. if w='pressure', l='2', returns [pr, re, es ..., re])
        """
        #return all unique substrings of a word w of length l from 1 letter to the entire word
        substrings = set([])
        for i in range(len(w)):
            sub = w[i:(i+l)]
            if len(sub) < l:
                continue
            substrings.update(['.'.join(sub)])
        return substrings

    def khorsi(self, word1, word2, freq_base, string_type):
        """Calculate the string similarity of two words given a set of characters and their frequencies in a corpus, Returns the value (implementation of Khorsi (2012))

        Parameters
        ----------
        w1: Word
            Either a string or list of transcription characters
        w2: Word
            Same as w1
        freq_base: dictionary
            a dictionary where each segment is mapped to its frequency of occurrence in a corpus
        string_type: string
            The type of segments to be used ('spelling' = Roman letters, 'transcription' = IPA symbols)

        Returns
        -------
        int
            A number representing the relatedness of two words based on Khorsi (2012)
        """
        if isinstance(word1, str):
            word1 = self.corpus.find(word1)
            w1 = getattr(word1, string_type)
        else:
            try:
                w1 = getattr(word1, string_type)
            except:
                w1 = word1

        if isinstance(word2, str):
            word2 = self.corpus.find(word2)
            w2 = getattr(word2, string_type)
        else:
            try:
                w2 = getattr(word2, string_type)
            except:
                w2 = word2

        longComSeq = self.lcs(w1, w2)
        if longComSeq == None:
            return None
        else:
            longest, left_over = longComSeq

        if isinstance(longest, str) and isinstance(left_over, str):
            longest = re.sub("[\W\d]", "", longest.strip())
            left_over = re.sub("[\W\d]", "", left_over.strip())
        else:
            pass
        total_freq = sum(value for value in freq_base.values())

        #Khorsi's algorithm
        try:
            if isinstance(w1, str):
                sum1 = sum(math.log(1/(freq_base[letter]/total_freq)) for letter in longest)
                sum2 = sum(math.log(1/(freq_base[letter]/total_freq)) for letter in left_over)
            else:
                sum1 = sum(math.log(1/(freq_base[seg.symbol]/total_freq)) for seg in longest)
                sum2 = sum(math.log(1/(freq_base[seg.symbol]/total_freq)) for seg in left_over)
        except ZeroDivisionError: # This occurred because a spelling string is being compared to a transcription freq_base
            w1, w2 = self.corpus.find(word1), self.corpus.find(word2)
            return self.khorsi(w1, w2, freq_base, string_type)

        return sum1-sum2

    def make_freq_base(self, string_type, count_what = 'type'):
        """Returns a dictionary of segments mapped to their frequency of occurrence in a corpus

        Parameters
        ---------
        string_type: string
            The type of segments to be used ('spelling' = Roman letters, 'transcription' = IPA symbols)
        count_what: string
            The type of frequency, either 'type' or 'token', defaults to 'type'

        Returns
        -------
        dictionary
            A dictionary where a segments maps to its frequency of occurrence in a corpus
        """
        self.count_what = count_what
        freq_base = collections.defaultdict(int)

        for word in self.corpus:
            if self.count_what == 'token':
                #frequency = word.frequency
                if self.corpus.name.lower() == 'iphod':
                    frequency = word.abs_freq
                else: #it's a custom corpus
                    frequency = word.frequency

            word = getattr(word, string_type)
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

    def mass_relate(self, query, string_type='spelling', count_what='type'):
        """Given an input Word, uses a corpus to calculate the relatedness of all other words in the corpus to that input Word

        Parameters
        ----------
        query: Word
            Either a string or list of segments representing a word in a corpus
        string_type: string
            The type of segments to be used ('spelling' = roman letters, 'transcription' = IPA symbols), defaults to 'spelling'
        count_what: string
            The type of frequency, either 'type' or 'token', defaults to 'type'

        Returns
        -------
        list
            a list of all words in a corpus with their respective relatedness score to the input word w in a writeable format for .txt files
        """
        self.count_what = count_what
        targ_word = self.corpus.find(query)
        freq_base = self.make_freq_base(string_type, count_what)
        relate = list()
        for word in self.corpus:
            #Skip over words that do not exist in corpus
            if word is None:
                continue
            relatedness = self.khorsi(targ_word, word, freq_base, string_type)
            if relatedness is None: #Skip over words that do not have a transcription in the corpus
                continue

            relate.append( (relatedness, word) )

        #Sort the list by most related
        relate.sort(key=lambda t:t[0])
        relate.reverse()

        return relate

    def get_word_string_type(self, w1, w2, string_type):
        if string_type == 'spelling':
            try:
                w1 = getattr(w1, string_type)
                w2 = getattr(w2, string_type)
                return w1, w2
            except:
                return w1, w2
        else:
            try:
                w1_trans = getattr(w1, string_type)
                w2_trans = getattr(w2, string_type)
                w1 = ''.join([seg.symbol for seg in w1_trans])
                w2 = ''.join([seg.symbol for seg in w2_trans])
                return w1, w2
            except:
                try:
                    word1 = self.corpus.find(w1)
                    w1_trans= getattr(word1, string_type)
                    w1 = ''.join([seg.symbol for seg in w1_trans])
                except: #No transcription available
                    w1 = 'N/A'
                try:
                    word2 = self.corpus.find(w2)
                    w2_trans = getattr(word2, string_type)
                    w2 = ''.join([seg.symbol for seg in w2_trans])
                except: # No transcription available
                    w2 = 'N/A'
            return w1, w2

    def __init__(self, corpus):
        """Initialize a Relator object by utilizing an already made corpus

        Parameters
        ----------
        corpus: Corpus
            The corpus to use

        Returns
        -------
        None
        """
        self.corpus = corpus
