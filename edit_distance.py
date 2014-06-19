import math
import collections
import re
import time
from codecs import open

import corpustools
from phono_align_ex import Aligner

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
            self.factory = corpustools.CorpusFactory()
            self.corpus = self.factory.make_corpus(corpus_name, features='spe', size='all')
            end_time = time.time()
            print('Corpus Complete')
            print('Corpus creation time: ' + str(end_time-start_time))



    def edit_distance(self, w1, w2, features_tf=True, features=None):
        """       
        TO-DO
        """
        if features == None:
            features = self.corpus.specifier.matrix
        a = Aligner(features_tf=features_tf, features=features)
        m = a.make_similarity_matrix(w1.transcription, w2.transcription)
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


if __name__ == '__main__':
    ## TESTING
    r = Relator(corpus_name='Iphod')
    ed = r.edit_distance(r.corpus['ship'], r.corpus['shopping'], features_tf=False)
    print(ed)