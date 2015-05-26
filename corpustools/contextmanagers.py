from corpustools.exceptions import PCTError

class BaseCorpusContext(object):
    def __init__(self, corpus, sequence_type, type_or_token):
        self.sequence_type = sequence_type
        self.type_or_token = type_or_token
        self.corpus = corpus

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

class MostFrequentVariantContext(BaseCorpusContext):

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

class CountTokenVariantContext(BaseCorpusContext):
    def __init__(self, corpus):
        self.corpus = corpus

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)

class RelativeTypeVariantContext(BaseCorpusContext):
    def __init__(self, corpus):
        self.corpus = corpus

    def __exit__(self, exc_type, exc, exc_tb):
        BaseCorpusContext.__exit__(self, exc_type, exc, exc_tb)
