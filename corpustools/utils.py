import random

from corpustools.corpus.classes.spontaneous import WordToken, Discourse

def generate_discourse(corpus):
    d = Discourse(name = '{} discourse'.format(corpus.name))
    lookup_list = list()
    for k in corpus.keys():
        lookup_list.extend([k for x in range(int(corpus[k].frequency))])
    random.shuffle(lookup_list)
    end = None
    for i, k in enumerate(lookup_list):
        wordtoken = WordToken(word = corpus[k],begin = i)
        d.add_word(wordtoken)

    return d


