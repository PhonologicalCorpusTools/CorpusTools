from corpustools.exceptions import PCTError, PCTPythonError

from corpustools.corpus.classes.lexicon import Word

class BaseCorpusContext(object):
    def __init__(self, corpus, sequence_type, type_or_token, attribute = None):
        self.sequence_type = sequence_type
        self.type_or_token = type_or_token
        self.corpus = corpus
        self.attribute = attribute

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc, exc_tb):
        if exc_type is None:
            return True
        #Do cleanup
        if not issubclass(exc_type,PCTError):
            raise(PCTPythonError(exc))


class CanonicalVariantContext(BaseCorpusContext):

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

    def __iter__(self):
        for w in self.corpus:
            w2 = w.__getstate__()
            w2['tier'] = w2[self.sequence_type]
            if self.type_or_token == 'type':
                w2['frequency'] = 1
            w2 = Word(**w2)
            yield w2

class MostFrequentVariantContext(BaseCorpusContext):

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

class CountTokenVariantContext(BaseCorpusContext):
    def __init__(self, corpus, sequence_type, attribute = None):
        BaseCorpusContext.__init__(self, corpus, sequence_type, 'token', attribute)

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

class RelativeTypeVariantContext(BaseCorpusContext):
    def __init__(self, corpus, sequence_type, attribute = None):
        BaseCorpusContext.__init__(self, corpus, sequence_type, 'type', attribute)

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)
