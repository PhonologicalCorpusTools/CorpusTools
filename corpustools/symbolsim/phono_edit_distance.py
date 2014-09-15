import math
import collections
import re
import time
from codecs import open

from corpustools.symbolsim.phono_align_ex import Aligner

class Relator(object):
    """Attributes: factory, corpus
    """

    def __init__(self, corpus):
        """Initialize a Relator object by utilizing an already made corpus

        Parameters
        ----------
        corpus_name: string
            The corpus to use

        Returns
        -------
        None
        """
        self.corpus = corpus

    def phono_edit_distance(self, word1, word2, string_type, features_tf=True, features=None):
        """Returns an analogue to Levenshtein edit distance but with the option of counting phonological features instead of characters

        Parameters:
        w1: string
            A string containing a transcription which will be compared to another string containing a transcription
        w2: string
            The other string containing a transcription to which w1 will be compared
        features_tf: boolean
            Set to True if edit_distance using phonological features is desired or False for only characters
        features: phonological features
            Features are the set feature specifications currently be used in the corpus (i.e. Hayes, SPE, etc.)
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


        if features == None:
            features = self.corpus.specifier
        a = Aligner(features_tf=features_tf, features=features)

        m = a.make_similarity_matrix(w1, w2)

        return m[-1][-1]['f']


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
        relate = list()
        for word in self.corpus:
            #Skip over words that do not have exist in corpus
            if word is None:
                continue
            relatedness = [self.phono_edit_distance(targ_word, word, string_type)]
            relate.append( (relatedness, word) )
        #Sort the list by most morphologically related
        relate.sort(key=lambda t:t[0])

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
