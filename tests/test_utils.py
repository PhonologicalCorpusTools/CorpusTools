
from corpustools.utils import generate_discourse

from corpustools.corpus.classes import Discourse

def test_discourse_generate(unspecified_test_corpus):
    d = generate_discourse(unspecified_test_corpus)
    assert(isinstance(d, Discourse))
