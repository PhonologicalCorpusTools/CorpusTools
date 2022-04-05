import random
import copy


from corpustools.corpus.classes.spontaneous import WordToken, Discourse

def generate_discourse(corpus):
    kwargs = dict(name=f'{corpus.name} discourse',
                  wav_path=corpus.wav_path)
    for a in corpus.attributes:
        if a.att_type == 'tier':
            kwargs['transcription_name'] = a.name
        elif a.att_type == 'spelling':
            kwargs['spelling_name'] = a.name
        if 'transcription_name' in kwargs and 'spelling_name' in kwargs:
            break

    d = Discourse(kwargs=kwargs)
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


