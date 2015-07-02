
from corpustools.gui.ppgui import *

from corpustools.gui.models import CorpusModel

def test_ppgui(qtbot, specified_test_corpus, settings):
    dialog = PPDialog(None, settings,CorpusModel(specified_test_corpus, settings), True)
    qtbot.addWidget(dialog)

    dialog.oneNonwordRadio.clicked.emit()
    assert(dialog.compType == 'nonword')
    dialog.fileRadio.clicked.emit()
    assert(dialog.compType == 'file')

    dialog.oneWordRadio.clicked.emit()
    assert(dialog.compType == 'one')
    dialog.algorithmWidget.widgets[0].setChecked(True)
    assert(dialog.algorithmWidget.value() == 'vitevitch')
    assert(dialog.typeTokenWidget.widgets[0].isEnabled())
    dialog.oneWordEdit.setText('atema')
    kwargs = dialog.generateKwargs()
    assert(kwargs['algorithm'] == 'vitevitch')
    assert(kwargs['sequence_type'] == 'transcription')
    assert(kwargs['query'][0].spelling == 'atema')
    assert(kwargs['probability_type'] == 'bigram')

    dialog.allwordsRadio.clicked.emit()
    assert(dialog.compType == 'all')
    dialog.algorithmWidget.widgets[0].setChecked(True)
    assert(dialog.algorithmWidget.value() == 'vitevitch')
    dialog.columnEdit.setText('test')
    dialog.probabilityTypeWidget.click(1)
    kwargs = dialog.generateKwargs()
    assert(kwargs['algorithm'] == 'vitevitch')
    assert(kwargs['sequence_type'] == 'transcription')
    assert(kwargs['probability_type'] == 'unigram')
    assert(kwargs['attribute'].display_name == 'test')
    assert(kwargs['attribute'].att_type == 'numeric')
