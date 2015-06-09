from corpustools.exceptions import PCTError, PCTPythonError
import math
import time
import collections
import copy

from corpustools.corpus.classes.lexicon import Word

class BaseCorpusContext(object):
    def __init__(self, corpus, sequence_type, type_or_token, attribute = None):
        self.sequence_type = sequence_type
        self.type_or_token = type_or_token
        self.corpus = corpus
        self.attribute = attribute
        self._freq_base = dict()

    def __enter__(self):
        pass
        
    def get_frequency_base(self, gramsize = 1, halve_edges=False, probability = False):
        """
        Generate (and cache) frequencies for each segment in the Corpus.

        Parameters
        ----------
        halve_edges : boolean
            If True, word boundary symbols ('#') will only be counted once
            per word, rather than twice.  Defaults to False.

        gramsize : integer
            Size of n-gram to use for getting frequency, defaults to 1 (unigram)

        probability : boolean
            If True, frequency counts will be normalized by total frequency,
            defaults to False

        Returns
        -------
        dict
            Keys are segments (or sequences of segments) and values are
            their frequency in the Corpus
        """
        print('hello')
        if (gramsize) not in self._freq_base:
            freq_base = collections.defaultdict(float)
            for word in self:
                seq = ['#'] + [x for x in getattr(word, self.sequence_type)] + ['#']
                grams = zip(*[seq[i:] for i in range(gramsize)])
                for x in grams:
                    if len(x) == 1:
                        x = x[0]
                    freq_base[x] += word.frequency
            freq_base['total'] = sum(value for value in freq_base.values())
            self._freq_base[(gramsize)] = freq_base
        print('whaddup')
        time.sleep(2)
        freq_base = self._freq_base[(gramsize)]
        return_dict = { k:v for k,v in freq_base.items()}
        if halve_edges and '#' in return_dict:
            return_dict['#'] = (return_dict['#'] / 2) + 1
            if not probability:
                return_dict['total'] -= return_dict['#'] - 2
        if probability:
            return_dict = { k:v/freq_base['total'] for k,v in return_dict.items()}
        return return_dict

    def get_phone_probs(self, gramsize = 1, probability = True, preserve_position = True, log_count = True):
        """
        Generate (and cache) phonotactic probabilities for segments in
        the Corpus.

        Parameters
        ----------
        gramsize : integer
            Size of n-gram to use for getting frequency, defaults to 1 (unigram)

        probability : boolean
            If True, frequency counts will be normalized by total frequency,
            defaults to False

        preserve_position : boolean
            If True, segments will in different positions in the transcription
            will not be collapsed, defaults to True

        log_count : boolean
            If True, token frequencies will be logrithmically-transformed
            prior to being summed

        Returns
        -------
        dict
            Keys are segments (or sequences of segments) and values are
            their phonotactic probability in the Corpus
        """
        if (gramsize, probability, preserve_position, log_count) not in self._freq_base:
            freq_base = collections.defaultdict(float)
            totals = collections.defaultdict(float)
            for word in self:
                freq = word.frequency
                if log_count:
                    freq = math.log(freq)
                grams = zip(*[getattr(word, self.sequence_type)[i:] for i in range(gramsize)])
                for i, x in enumerate(grams):
                    #if len(x) == 1:
                    #    x = x[0]
                    if preserve_position:
                        x = (x,i)
                        totals[i] += freq
                    freq_base[x] += freq

            if not preserve_position:
                freq_base['total'] = sum(value for value in freq_base.values())
            else:
                freq_base['total'] = totals
            self._freq_base[(gramsize, probability, preserve_position, log_count)] = freq_base
            
        freq_base = self._freq_base[(gramsize, probability,preserve_position, log_count)]
        return_dict = { k:v for k,v in freq_base.items()}
        if probability and not preserve_position:
            return_dict = { k:v/freq_base['total'] for k,v in return_dict.items()}
        elif probability:
            return_dict = { k:v/freq_base['total'][k[1]] for k,v in return_dict.items() if k != 'total'}
        return return_dict
        
    def __exit__(self, exc_type, exc, exc_tb):
        if exc_type is None:
            return True
        #Do cleanup
        if not issubclass(exc_type,PCTError):
            raise(PCTPythonError(exc))


class CanonicalVariantContext(BaseCorpusContext):
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

    def __iter__(self):
        for w in self.corpus:
            w = copy.copy(w)
            if self.type_or_token == 'type':
                w.frequency = 1
            yield w

class MostFrequentVariantContext(BaseCorpusContext):
    
    def __enter__(self):
        if not self.corpus.has_wordtokens:
            print('Advisory: Calling variants on a corpus without variants doesn''t make any sense!')
            error
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)
    
    def __iter__(self):
        for w in self.corpus:
            v = w.variants(self.sequence_type)
            w = copy.copy(w)
            if len(v.keys()) > 0:                                       # Set sequence type to the most frequent variant
                setattr(w, self.sequence_type, max(v.keys(), key=lambda k: v[k]))
            if self.type_or_token == 'type':
                w.frequency = 1
            yield w

class SeparatedTokensVariantContext(BaseCorpusContext):
    
    def __enter__(self):
        if not self.corpus.has_wordtokens:
            print('Advisory: Calling variants on a corpus without variants doesn''t make any sense!')
            error
        return self
        
    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)
        
    def __iter__(self):
        for i, word in enumerate(self.corpus):
            variants = word.variants()
            for v in variants:                                      # Create a new word from each variant
                if self.sequence_type == 'spelling':
                    spell = v
                    trans = getattr(word, 'transcription')
                    freq = variants[v]
                else:
                    spell = getattr(word, 'spelling')
                    trans = v
                    freq = variants[v]
                if self.type_or_token == 'type':
                    freq = 1
                w = Word(spelling = spell, transcription = trans, frequency = freq)
                yield w


class WeightedVariantContext(BaseCorpusContext):
    
    def __enter__(self):
        if not self.corpus.has_wordtokens:
            print('Advisory: Calling variants on a corpus without variants doesn''t make any sense!')
            error
        return self
            
    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)
        
    def __iter__(self):
        for i, word in enumerate(self.corpus):
            variants = word.variants()
            num_of_variants = len(variants)
            total_variants = sum(variants.values())
            for v in variants:                                      # Create a new word from each variant
                if self.sequence_type == 'spelling':
                    spell = v
                    trans = getattr(word, 'transcription')
                    freq = variants[v]/total_variants
                else:
                    spell = getattr(word, 'spelling')
                    trans = v
                    freq = variants[v]/total_variants
                if self.type_or_token == 'type':
                    freq = 1/num_of_variants
                w = Word(spelling = spell, transcription = trans, frequency = freq)
                yield w

