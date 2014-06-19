import math
import collections
import re
import time
from codecs import open

import corpustools

class Relator(object):
    """Initializes the string similarity relator based off the algorithm of morphological relatedness found in Khorsi (2012)
    
    Parameters
    ----------
    object: list
        contains parameters needed for the corpus which will be used in relating elements, some examples could be a corpus name or an already created corpus
    Returns
    -------
    Returns a relator type which can be used to call methods
    """

    def edit_distance(self, w1, w2):
        """Calculate the edit distance of two words given a set of characters and their frequencies in a corpus, Returns the value (implementation of Khorsi (2012))
        
        Parameters
        ----------
        w1: Word
            Either a string or list of transcription characters
        w2: Word
            Same as w1
        freq_base: dictionary
            a dictionary where each segment is mapped to its frequency of occurence in a corpus
        
        Returns
        -------
        int
            A number representing the relatedness of two words based on Khorsi (2012)
        """
        try:
    
            return edit_distance_score
        
        except ZeroDivisionError: #This happened because a spelling string is being compared to a transcription frequency base
            word1 =  self.corpus.find(w1)
            word2 = self.corpus.find(w2)
            w1 = getattr(word1, 'transcription')
            w2 = getattr(word2, 'transcription')
            
            edit_distance_score = 0
            
            return edit_distance_score



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
        word = self.corpus.find(query)
        w = getattr(word, string_type)
        relate = list()
        for word in self.corpus:
            word = getattr(word, string_type)
            #Skip over words that do not have transcriptions if string == 'transcription'
            if word is None:
                continue
            relatedness = [self.edit_distance(w, word)]
            relate.append( (relatedness, word) )
        #Sort the list by most morphologically related
        relate.sort(key=lambda t:t[0])
        relate.reverse()
        
        comp_strings = list()
        for score, word in relate:
            if not isinstance(word, str):
                word = ''.join([seg.symbol for seg in word])
            comp_strings.append( (word, score) )
            
        related_data = comp_strings
        return related_data


    def __init__(self,corpus_name=None, ready_made_corpus=None):
        """Initialize a Relator object by building a corpus or utilizing an already make corpus
        
        Parameters
        ----------
        corpus_name: string
            The corpus name, e.g. 'Iphod'
        ready_made_corpus: Corpus
            A corpus that has been built, if none provided, __init__ will build one
            
        Returns
        -------
        None
        """
        if ready_made_corpus is not None:
            self.corpus = ready_made_corpus
            return
        else:
            print('Building Corpus')
            start_time = time.time()
            self.factory = corpustools.CorpusFactory()
            self.corpus = self.factory.make_corpus(corpus_name, features='spe', size='all')
            end_time = time.time()
            print('Corpus Complete')
            print('Corpus creation time: ' + str(end_time-start_time))

if __name__ == '__main__':
    pass