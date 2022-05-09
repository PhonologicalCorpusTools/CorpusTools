
import pytest
import os

from corpustools.corpus.classes import Speaker

from corpustools.corpus.io.helper import AnnotationType, Annotation, BaseAnnotation

from corpustools.corpus.io.pct_textgrid import (textgrid_to_data,load_textgrid,
                                            guess_tiers)

#def test_guess_tiers(textgrid_test_dir):
#    tg = load_textgrid(os.path.join(textgrid_test_dir,'phone_word.TextGrid'))
#    result = guess_tiers(tg)
#    assert(result[0] == ['word'])
#    assert(result[1] == ['phone'])
#    assert(result[2] == [])

def test_basic(textgrid_test_dir):
    speaker = Speaker(None)
    path = os.path.join(textgrid_test_dir,'phone_word.TextGrid')
    data = textgrid_to_data(path, [AnnotationType('word','phone',None, anchor=True),
                                AnnotationType('phone',None,None, base=True)])
    expected_words = []

    a = Annotation('')
    a.references.append('phone')
    a.begins.append(0)
    a.ends.append(1)
    expected_words.append(a)

    a = Annotation('a')
    a.references.append('phone')
    a.begins.append(1)
    a.ends.append(3)
    expected_words.append(a)

    a = Annotation('')
    a.references.append('phone')
    a.begins.append(3)
    a.ends.append(4)
    expected_words.append(a)
    assert(data['word']._list == expected_words)

    assert(data['phone']._list == [BaseAnnotation('#', 0, 0.25),
                        BaseAnnotation('a', 0.25, 0.5),
                        BaseAnnotation('b', 0.5, 0.75),
                        BaseAnnotation('#', 0.75, 1)])

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
