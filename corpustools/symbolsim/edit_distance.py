import math
import collections
import re
import time
from codecs import open

from corpustools.corpus.classes import CorpusFactory
from corpustools.symbolsim.phono_align_ex import Aligner

class Relator(object):
    """Attributes: factory, corpus
    """

    def __init__(self, corpus_name=None, ready_made_corpus=None):
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
            self.factory = CorpusFactory()
            self.corpus = self.factory.make_corpus(corpus_name, features='spe', size='all')
            end_time = time.time()
            print('Corpus Complete')
            print('Corpus creation time: ' + str(end_time-start_time))

    def edit_distance(self, s1, s2, string_type):
        """Returns the Levenshtein edit distance between two strings s1 and s2, code drawn from http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python.
        The number is the number of operations needed to transform s1 into s2, three operations are possible: insert, delete, substitute
        
        Parameters
        ----------
        s1: string
            the first string to be compared
        s2: string
            the second string to be compared
        
        Returns
        -------
        int:
            the edit distance between two strings 
        """
        if string_type == 'transcription':
            try:
                w1, w2 = self.corpus.find(s1), self.corpus.find(s2)
                s1, s2 = getattr(w1, string_type), getattr(w2, string_type)
            except: #This occurred because the input string is already a transcription
                pass
        if s1 is None or s2 is None:
            return None
        elif len(s1) < len(s2):
            return self.edit_distance(s2, s1, string_type)

        if len(s2) == 0:
            return len(s1)
     
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1       # than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
     
        return previous_row[-1]
    
    
    def phono_edit_distance(self, word1, word2, string_type, features_tf=False, features=None):
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
        try:
            w1 = getattr(word1, string_type)
            w2 = getattr(word2, string_type)
        except: #This occurred because word1 not a Word object and is likely a list containing a transcription
            w1 = word1
            w2 = word2
        if features == None:
            features = self.corpus.specifier.matrix
        a = Aligner(features_tf=features_tf, features=features)
        #try:
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
            relatedness = [self.edit_distance(targ_word, word, string_type)]
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
                
                
if __name__ == '__main__':
    ## TESTING
    r = Relator(corpus_name='Iphod')
    ed = r.phono_edit_distance(r.corpus['ship'], r.corpus['shopping'], features_tf=False)
    print(ed)
