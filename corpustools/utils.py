import random
import copy


from corpustools.corpus.classes.spontaneous import WordToken, Discourse

def generate_discourse(corpus):
    d = Discourse(name = '{} discourse'.format(corpus.name))
    lookup_list = list()
    for k in corpus.keys():
        lookup_list.extend([k for x in range(int(corpus[k].frequency))])
    random.shuffle(lookup_list)
    end = None
    d.lexicon = copy.deepcopy(corpus)
    for k in d.lexicon.keys():
        d.lexicon[k].wordtokens = list()
    for i, k in enumerate(lookup_list):
        wordtoken = WordToken(word = d.lexicon[k],begin = i)
        d.lexicon[k].wordtokens.append(wordtoken)
        d.add_word(wordtoken)

    return d


