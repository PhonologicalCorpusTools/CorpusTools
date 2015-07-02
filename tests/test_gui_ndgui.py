
from corpustools.gui.ndgui import *

from corpustools.gui.models import CorpusModel

def test_ndgui(qtbot, specified_test_corpus, settings):
    dialog = NDDialog(None, settings,CorpusModel(specified_test_corpus, settings), True)
    qtbot.addWidget(dialog)

    dialog.oneNonwordRadio.clicked.emit()
    assert(dialog.compType == 'nonword')
    dialog.fileRadio.clicked.emit()
    assert(dialog.compType == 'file')

    dialog.oneWordRadio.clicked.emit()
    assert(dialog.compType == 'one')
    dialog.algorithmWidget.click(0)
    assert(dialog.algorithmWidget.value() == 'edit_distance')
    assert(not dialog.typeTokenWidget.widgets[0].isEnabled())
    dialog.oneWordEdit.setText('atema')
    kwargs = dialog.generateKwargs()
    assert(kwargs['algorithm'] == 'edit_distance')
    assert(kwargs['sequence_type'] == 'spelling')
    assert(kwargs['query'][0].spelling == 'atema')
    assert(kwargs['max_distance'] == 1)

    dialog.allwordsRadio.clicked.emit()
    assert(dialog.compType == 'all')
    dialog.algorithmWidget.click(0)
    assert(dialog.algorithmWidget.value() == 'edit_distance')
    assert(not dialog.typeTokenWidget.widgets[0].isEnabled())
    dialog.columnEdit.setText('test')
    kwargs = dialog.generateKwargs()
    assert(kwargs['algorithm'] == 'edit_distance')
    assert(kwargs['sequence_type'] == 'spelling')
    assert(kwargs['max_distance'] == 1)
    assert(kwargs['attribute'].display_name == 'test')
    assert(kwargs['attribute'].att_type == 'numeric')

