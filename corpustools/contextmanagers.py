from corpustools.exceptions import PCTError, PCTPythonError
import math
import collections
import copy
import operator

from corpustools.corpus.classes.lexicon import Word

from corpustools.exceptions import PCTContextError

def ensure_context(context):
    if not isinstance(context, BaseCorpusContext):
        raise(PCTContextError('Context manager required for here, please see API documentation for more details.'))

class BaseCorpusContext(object):
    """
    Abstract Corpus context class that all other contexts inherit from.

    Parameters
    ----------
    corpus : Corpus
        Corpus to form context from
    sequence_type : str
        Sequence type to evaluate algorithms on (i.e., 'transcription')
    type_or_token : str
        The type of frequency to use for calculations
    attribute : Attribute, optional
        Attribute to save results to for calculations involving all words
        in the Corpus
    frequency_threshold: float, optional
        If specified, ignore words below this token frequency
    """
    def __init__(self, corpus, sequence_type, type_or_token, attribute=None, frequency_threshold=0, log_count=True):
        self.sequence_type = sequence_type
        self.type_or_token = type_or_token
        self.corpus = corpus
        self.name = self.corpus.name
        self.attribute = attribute
        self._freq_base = {}
        self.length = None
        self.frequency_threshold = frequency_threshold
        self.log_count = log_count

    @property
    def inventory(self):
        return self.corpus.inventory

    @property
    def specifier(self):
        return self.corpus.specifier

    def __enter__(self):
        if self.attribute is not None:
            self.corpus.add_attribute(self.attribute,initialize_defaults = False)
        return self

    def __len__(self):
        if self.length is not None:
            return self.length
        else:
            counter = 0
            for w in self:
                counter += 1
            self.length = counter
            return self.length

    def get_frequency_base(self, gramsize=1, halve_edges=False, probability=False, need_wb=True):
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

        need_wb : boolean
            If True, word boundaries are added. Defaults to True.
            False if e.g., for env filter in mutual information

        Returns
        -------
        dict
            Keys are segments (or sequences of segments) and values are
            their frequency in the Corpus
        """
        if (gramsize) not in self._freq_base:
            freq_base = collections.defaultdict(float)
            for word in self:
                tier = getattr(word, self.sequence_type)
                if self.sequence_type.lower() == 'spelling':
                    seq = ['#'] + [x for x in tier] + ['#']
                elif need_wb:       # if each word should have word boundaries
                    if halve_edges:   # and only at the end of the word (word boundary is counted only once per word)
                        seq = tier.list + ['#']
                    else:             # WB on both sides of the word
                        seq = tier.with_word_boundaries()
                else:
                    seq = tier.list
                grams = zip(*[seq[i:] for i in range(gramsize)])
                for x in grams:
                    if len(x) == 1:
                        x = x[0]
                    freq_base[x] += word.frequency
            freq_base['total'] = sum(value for value in freq_base.values())
            self._freq_base[(gramsize)] = freq_base
        freq_base = self._freq_base[(gramsize)]
        return_dict = { k:v for k,v in freq_base.items()}
        # if halve_edges and '#' in return_dict:
        #     return_dict['#'] = (return_dict['#'] / 2) + 1
        #     if not probability:
        #         return_dict['total'] -= return_dict['#'] - 2
        if probability:
            return_dict = { k:v/freq_base['total'] for k,v in return_dict.items()}
        return return_dict

    def get_phone_probs(self, gramsize = 1, probability = True, preserve_position = True):
        """
        Generate (and cache) phonotactic probabilities for segments in
        the Corpus.

        Parameters
        ----------
        gramsize : integer
            Size of n-gram to use for getting frequency, defaults to 1 (unigram)

        probability : boolean
            If True, frequency counts will be normalized by total frequency,
            defaults to True

        preserve_position : boolean
            If True, segments in different positions in the transcription
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
        if (gramsize, preserve_position, self.log_count) not in self._freq_base:
            freq_base = collections.defaultdict(float)
            totals = collections.defaultdict(float)
            for word in self:
                if self.type_or_token == 'type':
                    freq = 1
                elif self.type_or_token == 'token' and self.log_count:
                    freq = math.log(word.frequency) if word.frequency > 1 else math.log(1.00001)
                else:
                    freq = word.frequency

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
            self._freq_base[(gramsize, preserve_position, self.log_count)] = freq_base

        freq_base = self._freq_base[(gramsize,preserve_position, self.log_count)]
        return_dict = { k:v for k,v in freq_base.items()}
        if probability and not preserve_position:
            return_dict = { k:v/freq_base['total'] for k,v in return_dict.items()}
        elif probability:
            return_dict = { k:v/freq_base['total'][k[1]]
                            for k,v in return_dict.items() if k != 'total'}
        return return_dict

    def __exit__(self, exc_type, exc, exc_tb):
        if exc_type is None:
            return True
        else:
            if self.attribute is not None:
                self.corpus.remove_attribute(self.attribute)


class CanonicalVariantContext(BaseCorpusContext):
    """
    Corpus context that uses canonical forms for transcriptions and tiers

    See the documentation of `BaseCorpusContext` for additional information
    """
    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

    def __iter__(self):
        for word in self.corpus:
            if self.type_or_token == 'token' and word.frequency == 0:
                continue
            if self.frequency_threshold > 0 and word.frequency < self.frequency_threshold:
                continue
            w = copy.copy(word)
            if math.isnan(word.frequency):
                w.frequency = 0
            elif self.type_or_token == 'type':
                w.frequency = 1
            w.original = word
            yield w

class MostFrequentVariantContext(BaseCorpusContext):
    """
    Corpus context that uses the most frequent pronunciation variants
    for transcriptions and tiers

    See the documentation of `BaseCorpusContext` for additional information
    """
    def __enter__(self):
        self = BaseCorpusContext.__enter__(self)
        if not self.corpus.has_wordtokens:
            raise(PCTError('The corpus specified does not have variants.'))
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

    def __iter__(self):
        for word in self.corpus:
            if self.type_or_token == 'token' and word.frequency == 0:
                continue
            if self.frequency_threshold > 0 and word.frequency < self.frequency_threshold:
                continue
            v = word.variants(self.sequence_type)
            w = copy.copy(word)
            if math.isnan(word.frequency):
                w.frequency = 0
            if len(v.keys()) > 0:                                       # Sort variants by most frequent
                v_sorted = sorted(v.items(), key=operator.itemgetter(1), reverse=True)
                if len(v_sorted) == 1:                                  # There's only 1 variant
                    setattr(w, self.sequence_type, v_sorted[0][0])
                elif v_sorted[0][1] != v_sorted[1][1]:                  # There's only one most frequent variant
                    setattr(w, self.sequence_type, v_sorted[0][0])
                else:                                                   # There're variants tied for frequency
                    highest_freq = v_sorted[0][1]
                    v_candidates = list()
                    for vv in v_sorted:
                        if vv[1] != highest_freq:
                            break
                        else:
                            v_candidates.append(vv[0])
                    if getattr(w, self.sequence_type) in v_candidates:  # Use cannonical variant if it is one of most frequent
                        pass
                    else:
                        v_longest1 = max(v_candidates, key=len)
                        v_candidates.reverse()
                        v_longest2 = max(v_candidates, key=len)
                        if v_longest1 == v_longest2:
                            setattr(w, self.sequence_type, v_longest1)  # Use longest variant if one exists
                        else:
                            v_candidates = [vv for vv in v_candidates if len(vv) == len(v_longest1)]
                            v_candidates = sorted(v_candidates)
                            setattr(w, self.sequence_type, v_candidates[0])  # Use longest variant that is first alphabetically

            if self.type_or_token == 'type':
                w.frequency = 1
            w.original = word
            yield w

class SeparatedTokensVariantContext(BaseCorpusContext):
    """
    Corpus context that treats pronunciation variants as separate types
    for transcriptions and tiers

    See the documentation of `BaseCorpusContext` for additional information
    """
    def __enter__(self):
        self = BaseCorpusContext.__enter__(self)
        if not self.corpus.has_wordtokens:
            raise(PCTError('The corpus specified does not have variants.'))
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

    def __iter__(self):
        for word in self.corpus:
            if math.isnan(word.frequency):
                continue
            if self.type_or_token == 'token' and word.frequency == 0:
                continue
            if self.frequency_threshold > 0 and word.frequency < self.frequency_threshold:
                continue
            variants = word.variants(self.sequence_type)
            for v in variants:                                      # Create a new word from each variant
                kwargs = {}
                if self.sequence_type == 'spelling':
                    kwargs['spelling'] = v
                    kwargs['transcription'] = word.transcription
                    kwargs['frequency'] = variants[v]
                elif self.sequence_type == 'transcription':
                    kwargs['spelling'] = word.spelling
                    kwargs['transcription'] = v
                    kwargs['frequency'] = variants[v]
                else:
                    kwargs['spelling'] = word.spelling
                    kwargs['transcription'] = word.transcription
                    kwargs['frequency'] = variants[v]
                    kwargs[self.sequence_type] = v
                if self.type_or_token == 'type':
                    kwargs['frequency'] = 1
                w = Word(**kwargs)
                yield w


class WeightedVariantContext(BaseCorpusContext):
    """
    Corpus context that weights frequency of pronunciation variants by the
    number of variants or the token frequency
    for transcriptions and tiers

    See the documentation of `BaseCorpusContext` for additional information
    """
    def __enter__(self):
        self = BaseCorpusContext.__enter__(self)
        if not self.corpus.has_wordtokens:
            raise(PCTError('The corpus specified does not have variants.'))
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

    def __iter__(self):
        for word in self.corpus:
            if math.isnan(word.frequency):
                continue
            if self.type_or_token == 'token' and word.frequency == 0:
                continue
            if self.frequency_threshold > 0 and word.frequency < self.frequency_threshold:
                continue
            variants = word.variants(self.sequence_type)
            num_of_variants = len(variants)
            total_variants = sum(variants.values())
            for v in variants:                                      # Create a new word from each variant
                kwargs = {}
                if self.sequence_type == 'spelling':
                    kwargs['spelling'] = v
                    kwargs['transcription'] = word.transcription
                    kwargs['frequency'] = variants[v]/total_variants
                elif self.sequence_type == 'transcription':
                    kwargs['spelling'] = word.spelling
                    kwargs['transcription'] = v
                    kwargs['frequency'] = variants[v]/total_variants
                else:
                    kwargs['spelling'] = word.spelling
                    kwargs['transcription'] = word.transcription
                    kwargs['frequency'] = variants[v]/total_variants
                    kwargs[self.sequence_type] = v
                if self.type_or_token == 'type':
                    kwargs['frequency'] = 1/num_of_variants
                w = Word(**kwargs)
                yield w

