
import pytest
import os

from corpustools.corpus.classes import Speaker

from corpustools.corpus.io.helper import AnnotationType

from corpustools.corpus.io.textgrid import (textgrids_to_data,textgrid_to_data,
                                            process_tier_name,load_textgrid,
                                            guess_tiers,
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

def test_guess_tiers(textgrid_test_dir):
    tg = load_textgrid(os.path.join(textgrid_test_dir,'phone_word.TextGrid'))
    result = guess_tiers(tg)
    assert(result[0] == ['word'])
    assert(result[1] == ['phone'])
    assert(result[2] == [])

def test_basic(textgrid_test_dir):
    speaker = Speaker(None)
    path = os.path.join(textgrid_test_dir,'phone_word.TextGrid')
    data = textgrid_to_data(path, [AnnotationType('word','phone',None, anchor=True),
                                AnnotationType('phone',None,None, base=True)])
    assert(data['word']._list == [{'label': '','token':{}, 'phone':(0,1)},
                        {'label': 'a','token':{}, 'phone':(1,3)},
                        {'label': '','token':{}, 'phone':(3,4)}])
    assert(data['phone']._list == [{'label':'', 'begin': 0, 'end': 0.25},
                        {'label':'a', 'begin': 0.25, 'end': 0.5},
                        {'label':'b', 'begin': 0.5, 'end': 0.75},
                        {'label':'', 'begin': 0.75, 'end': 1}])

@pytest.mark.xfail
def test_two_speakers(textgrid_test_dir):
    path = os.path.join(textgrid_test_dir,'2speakers.TextGrid')
    data = textgrid_to_data(path, [AnnotationType('Speaker 1 - word','Speaker 1 - phone',None, anchor=True, speaker = 'Speaker 1'),
                                AnnotationType('Speaker 1 - phone',None,None, base=True, speaker = 'Speaker 1'),
                                AnnotationType('Speaker 2 - word','Speaker 2 - phone',None, anchor=True, speaker = 'Speaker 2'),
                                AnnotationType('Speaker 2 - phone',None,None, base=True, speaker = 'Speaker 2')])
    data.collapse_speakers()
    print(data['word']._list)
    assert(data['word']._list == [{'label': '','token':{}, 'phone':(0,1)},
                        {'label': 'a','token':{}, 'phone':(1,3)},
                        {'label': 'b','token':{}, 'phone':(3,5)},
                        {'label': 'a','token':{}, 'phone':(5,7)},
                        {'label': 'c','token':{}, 'phone':(7,9)},
                        {'label': '','token':{}, 'phone':(9,10)}])
    assert(data['phone']._list == [{'label':'', 'begin': 0, 'end': 0.1},
                        {'label':'a', 'begin': 0.1, 'end': 0.2},
                        {'label':'b', 'begin': 0.2, 'end': 0.3},
                        {'label':'c', 'begin': 0.3, 'end': 0.4},
                        {'label':'d', 'begin': 0.4, 'end': 0.5},
                        {'label':'a', 'begin': 0.5, 'end': 0.6},
                        {'label':'b', 'begin': 0.6, 'end': 0.7},
                        {'label':'d', 'begin': 0.7, 'end': 0.8},
                        {'label':'e', 'begin': 0.8, 'end': 0.9},
                        {'label':'', 'begin': 0.9, 'end': 1}])
