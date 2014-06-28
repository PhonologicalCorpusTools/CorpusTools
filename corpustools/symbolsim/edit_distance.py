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



    def levenshtein(self, w1, w2, string_type = 'spelling'):
        """Calculate Levenshtein (1966) edit distance between two strings. Code was acquired from:
                    http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
        
        Parameters
        ----------
        w1: string
            Te first string to be compared
        w2: string
            The second string to which the first thing is compared to
            
        Returns
        -------
            The Levenshtein edit distance between two strings (i.e. the minimum number of operations needed to change one string into another using delete, insert or substitute)
        """
        if len(w1) < len(w2):
            return self.levenshtein(w2, w1)
     
        # len(s1) >= len(s2)
        if len(w2) == 0:
            return len(w1)
     
        previous_row = range(len(w2) + 1)
        for i, c1 in enumerate(w1):
            current_row = [i + 1]
            for j, c2 in enumerate(w2):
                insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1       # than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
     
        return previous_row[-1]
    
    def phono_edit_distance(self, w1, w2, features_tf=True, features=None):
        """Returns an analogue to Levenshtein edit distance but with phonological features instead of characters in a string
        
        Parameters:
        w1: string
            A string containing a transcription which will be compared to another string containing a transcription
        w2: string
            The other string containing a transcription to which w1 will be compared
        features_tf: boolean
        
        features: phonological features
            Features are the set feature specifications currently be used in the corpus (i.e. Hayes, SPE, etc.)
        """
        if features == None:
            features = self.corpus.specifier.matrix
        a = Aligner(features_tf=features_tf, features=features)
        #try:
        m = a.make_similarity_matrix(w1, w2)
        return m[-1][-1]['f']
        
        #except AttributeError: #This occured
        



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
            relatedness = [self.levenshtein(w, word)]
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


if __name__ == '__main__':
    ## TESTING
    r = Relator(corpus_name='Iphod')
    ed = r.edit_distance(r.corpus['ship'], r.corpus['shopping'], features_tf=False)
    print(ed)
