
import unittest
from collections import OrderedDict
from corpustools.gui.widgets import *

from .conftest import specified_test_corpus
from PyQt5.QtTest import QTest

def test_directory_widget(application):
    widget = DirectoryWidget()

    widget.setPath('test')

    assert(widget.value() == 'test')

def test_punctuation_widget(application):
    widget = PunctuationWidget(['.',',','-'])

    # Test value

    bs = widget.btnGroup.buttons()
    bs[0].setChecked(True)

    assert(widget.value() == ['.'])

    # Test check all

    widget.checkAll.clicked.emit()

    assert(widget.value() == ['.',',','-'])

    # Test uncheck all

    widget.uncheckAll.clicked.emit()

    assert(widget.value() == [])

def test_tier_widget(application, specified_test_corpus):
    # Test with spelling
    widget = TierWidget(specified_test_corpus, include_spelling = True)

    widget.tierSelect.setCurrentIndex(0)

    assert(widget.value() == 'spelling')
    assert(widget.displayValue() == 'Spelling')

    widget.tierSelect.setCurrentIndex(1)

    assert(widget.value() == 'transcription')
    assert(widget.displayValue() == 'Transcription')

    #Test disable spelling

    widget.setSpellingEnabled(False)

    widget.tierSelect.setCurrentIndex(0)

    assert(widget.value() == 'transcription')
    assert(widget.displayValue() == 'Transcription')

    # Test without spelling
    widget = TierWidget(specified_test_corpus, include_spelling = False)

    widget.tierSelect.setCurrentIndex(0)

    assert(widget.value() == 'transcription')
    assert(widget.displayValue() == 'Transcription')

def test_radio_select_widget(application):
    widget = RadioSelectWidget('', OrderedDict([('Option 1', 'option1'),('Option 2', 'option2')]))
    widget.initialClick()

    assert(widget.value() == 'option1')
    assert(widget.displayValue() == 'Option 1')

    widget.disable()
    assert(not widget.widgets[0].isEnabled())

    widget.enable()
    assert(widget.widgets[0].isEnabled())


def test_inventory_box(application, specified_test_corpus):
    widget = InventoryBox('Inventory', specified_test_corpus.inventory)

    widget.setExclusive(True)
    bs = widget.btnGroup.buttons()
    for b in bs:
        b.setChecked(True)
    assert(widget.value() == bs[-1].text())

    widget.clearAll()

    assert(widget.value() == '')

    widget.setExclusive(False)
    assert(widget.value() == [])
    for b in widget.btnGroup.buttons():
        b.setChecked(True)

    assert(set(widget.value()) == set([ x.symbol for x in specified_test_corpus.inventory]))

def test_transcription_widget(application, specified_test_corpus):
    widget = TranscriptionWidget('Transcription', specified_test_corpus.inventory)

    widget.setText('test')

    assert(widget.text(), 'test')

    widget.setText('')
    expected = []
    for b in widget.segments.btnGroup.buttons():
        b.clicked.emit()
        expected.append(b.text())


    assert(widget.text() == '.'.join(expected))

def test_feature_box(application, specified_test_corpus):
    widget = FeatureBox('Transcription', specified_test_corpus.inventory)

    # Test basic init

    assert(set(widget.features) == set(['EXTRA','LONG','ant','back','cont','cor',
                'del_rel','distr','glot_cl','hi_subgl_pr','high',
                'lat','low','mv_glot_cl','nasal','round','son',
                'strid','tense','voc','voice']))

    assert(set(widget.values) == set(['n','+','-','.']))

    f, v = widget.features[0], widget.values[0]

    f2, v2 = widget.features[1], widget.values[1]

    # Test default return value

    assert(widget.value() == '')

    # Test no action when no features selected

    b = widget.buttons[0]

    b.clicked.emit()

    assert(widget.value() == '')

    # Test single feature selected

    widget.featureList.setCurrentRow(0)

    b.clicked.emit()

    assert(widget.value() == '[{}{}]'.format(v,f))

    # Test multiple features selected

    widget.featureList.setCurrentRow(1)

    b2 = widget.buttons[1]

    b2.clicked.emit()

    assert(widget.value() == '[{}{},{}{}]'.format(v,f,v2,f2))

    # Test to ensure values are unique

    b2.clicked.emit()

    assert(widget.value() == '[{}{},{}{}]'.format(v,f,v2,f2))

    # Test clear all

    widget.clearButton.clicked.emit()

    assert(widget.value() == '')

    widget.featureList.setCurrentRow(0)
    b.clicked.emit()

    widget.featureList.setCurrentRow(1)
    b2.clicked.emit()

    widget.envList.setCurrentRow(0)

    widget.clearOneButton.clicked.emit()

    assert(widget.value() == '[{}{}]'.format(v2,f2))

def test_digraph_dialog(application):
    dialog = DigraphDialog(['a','b','c'])

    # Test init

    b = dialog.buttons[0]

    assert(b.text() == 'a')

    # Test character adding

    b.clicked.emit()

    assert(dialog.value() == 'a')

    # Test duplicates okay

    b.clicked.emit()

    assert(dialog.value() == 'aa')

def test_segment_pair_widget(application, specified_test_corpus):
    widget = SegmentPairSelectWidget(specified_test_corpus.inventory)

def test_environment_select_widget(application, specified_test_corpus):
    widget = EnvironmentSelectWidget(specified_test_corpus.inventory)

