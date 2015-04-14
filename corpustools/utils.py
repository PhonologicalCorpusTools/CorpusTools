import random
import copy
import shutil
import os

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

def make_htk_safe(string):
    if string.startswith("'"):
        string = '\\' + string
    return string

def export_pronunciation_dict(corpus, path, include_variants = True, min_rel_freq = 0.25):
    with open(path, 'w') as f:
        for w in corpus.iter_words_case_insensitive():
            orth = w.spelling.upper()
            if str(w.transcription) == '':
                continue
            f.write('{} {}\n'.format(make_htk_safe(orth), ' '.join(w.transcription).upper()))
            if not include_variants:
                continue
            variants = w.variants()
            for v, c in variants.items():
                if v == w.transcription:
                    continue
                if c/w.frequency < min_rel_freq:
                    continue
                f.write('{} {}\n'.format(make_htk_safe(orth), ' '.join(v).upper()))

def export_discourses_aligner(corpus, path, include_variants = True, min_rel_freq = 0.25):
    data_path = os.path.join(path,'data')
    dict_path = os.path.join(path, '{}.dict'.format(corpus.name))
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    export_pronunciation_dict(corpus.lexicon, dict_path)
    for k,v in corpus.discourses.items():
        filename = os.path.join(data_path, k + '.lab')
        with open(filename, 'w') as f:

            f.write(' '.join(make_htk_safe(w.spelling.upper()) for w in v if str(w.transcription) != ''))
        if v.has_audio:
            shutil.copyfile(v.wav_path, os.path.join(data_path,k + '.wav'))
