
import pytest
import os

from corpustools.corpus.classes import Speaker

from corpustools.corpus.io.textgrid import (textgrids_to_data,
                                            process_tier_name,load_textgrid,
                                            get_speaker_names)

def test_process_name():
    tier_names = [('Speaker 1 - Word', ('Speaker 1','Word')),
                        ('Word = Speaker 1',('Word','Speaker 1')),
                        ('Orthography (Speaker1)',('Orthography','Speaker1')),
                        ('Orthography (Speaker 1)',('Orthography','Speaker 1')),
                        ('Orthography (Speaker_1)',('Orthography','Speaker_1')),
                        ('Orthography',('Orthography',None))
                        ]
    for t in tier_names:
        assert(process_tier_name(t[0]) == t[1])

def test_speaker_names(textgrid_test_dir):
    tg = load_textgrid(os.path.join(textgrid_test_dir,'2speakers.TextGrid'))
    speakers = get_speaker_names(tg, 'word')
    assert(speakers == ['Speaker 1', 'Speaker 2'])

@pytest.mark.xfail
def test_basic(textgrid_test_dir):
    speaker = Speaker(None)
    expected = {'name':'phone_word',
                'data':{
                'phone':[{'label':'', 'begin': 0, 'end': 0.25},
                        {'label':'a', 'begin': 0.25, 'end': 0.5},
                        {'label':'b', 'begin': 0.5, 'end': 0.75},
                        {'label':'', 'begin': 0.75, 'end': 1}],
                'word': [{'label': 'a', 'phone':(0,1)},
                        {'label': 'a', 'phone':(1,3)},
                        {'label': 'a', 'phone':(3,4)}],
                'speaker': [{'label': None, 'phone':(0,4)}]}}
    path = os.path.join(textgrid_test_dir,'phone_word.TextGrid')
    data = textgrids_to_data(path, 'word','phone', None, None)
    for i, d in enumerate(data):
        print(expected[i])
        print(d)
        assert(expected[i] == d)
