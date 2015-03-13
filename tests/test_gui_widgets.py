

from corpustools.gui.widgets import *

def test_directory_widget(qtbot):
    print(qtbot)
    widget = DirectoryWidget()

    widget.setPath('test')

    assert(widget.value() == 'test')

def test_radio_select_widget():
    widget = RadioSelectWidget('', {'Option 1': 'option1','Option 2': 'option2'})
    assert(True)


def test_inventory_box(specified_test_corpus):
    widget = InventoryBox('Inventory', specified_test_corpus.inventory)

    widget.setExclusive(False)
    #for b in widget.btnGroup:
    #    b.click()

    #assert(set(widget.value()) == set(specified_test_corpus.inventory.keys()))


def test_transcription_widget(specified_test_corpus):
    widget = TranscriptionWidget('Transcription', specified_test_corpus.inventory)

def test_feature_box(specified_test_corpus):
    widget = FeatureBox('Transcription', specified_test_corpus.inventory)

def test_segment_pair_widget(specified_test_corpus):
    widget = SegmentPairSelectWidget(specified_test_corpus.inventory)

def test_environment_select_widget(specified_test_corpus):
    widget = EnvironmentSelectWidget(specified_test_corpus.inventory)
