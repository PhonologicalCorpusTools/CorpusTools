

from corpustools.gui.ssgui import *

from corpustools.gui.models import CorpusModel

def test_ssgui(qtbot, specified_test_corpus, settings):
    dialog = SSDialog(None, settings, CorpusModel(specified_test_corpus, settings), True)
    qtbot.addWidget(dialog)

    dialog.twoWordRadio.clicked.emit()
    assert(dialog.compType == 'two')
    dialog.fileRadio.clicked.emit()
    assert(dialog.compType == 'file')

    dialog.clearCreated()

    dialog.oneWordRadio.clicked.emit()
    assert(dialog.compType == 'one')
    dialog.algorithmWidget.click(0)
    assert(dialog.algorithmWidget.value() == 'edit_distance')
    assert(not dialog.typeTokenWidget.widgets[0].isEnabled())
    dialog.oneWordEdit.setText('atema')
    kwargs = dialog.generateKwargs()
    assert(kwargs['algorithm'] == 'edit_distance')
    assert(kwargs['sequence_type'] == 'spelling')
    assert(kwargs['query'].spelling == 'atema')
    assert(kwargs['min_rel'] is None)
    assert(kwargs['max_rel'] is None)

    dialog.algorithmWidget.click(2)
    assert(dialog.algorithmWidget.value() == 'khorsi')
    assert(dialog.typeTokenWidget.widgets[0].isEnabled())
    dialog.wordOneEdit.setText('atema')
    dialog.wordTwoEdit.setText('mata')
    dialog.minEdit.setText('20')
    dialog.maxEdit.setText('21')
    kwargs = dialog.generateKwargs()
    assert(kwargs['algorithm'] == 'khorsi')
    assert(kwargs['sequence_type'] == 'spelling')
    assert(kwargs['query'][0].spelling == 'atema', kwargs['query'][0].spelling == 'mata')
    assert(kwargs['min_rel'] == 20)
    assert(kwargs['max_rel'] == 21)
    assert(kwargs['type_token'] == 'type')

    dialog.algorithmWidget.click(1)
    assert(dialog.algorithmWidget.value() == 'phono_edit_distance')
    assert(not dialog.typeTokenWidget.widgets[0].isEnabled())
    dialog.wordOneEdit.setText('mata')
    dialog.wordTwoEdit.setText('atema')
    dialog.minEdit.setText('blahhhh')
    dialog.maxEdit.setText('blahhhh2')
    kwargs = dialog.generateKwargs()
    assert(kwargs['algorithm'] == 'phono_edit_distance')
    assert(kwargs['sequence_type'] == 'transcription')
    assert(kwargs['query'][0].spelling == 'mata', kwargs['query'][0].spelling == 'atema')
    assert(kwargs['min_rel'] is None)
    assert(kwargs['max_rel'] is None)

