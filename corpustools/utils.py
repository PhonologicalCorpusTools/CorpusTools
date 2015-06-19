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
    for i, k in enumerate(lookup_list):
        word = d.lexicon.get_or_create_word(spelling = corpus[k].spelling,
                                            transcription = corpus[k].transcription)
        word.frequency += 1
        wordtoken = WordToken(word = word,begin = i)
        d.lexicon[k].wordtokens.append(wordtoken)
        d.add_word(wordtoken)


    return d


