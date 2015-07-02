
from corpustools.gui.asgui import ASDialog

def test_asgui(qtbot, settings):
    dialog = ASDialog(None, settings, True)
    qtbot.addWidget(dialog)

    dialog.fileRadio.clicked.emit()
    assert(dialog.compType == 'file')

    dialog.oneDirectoryRadio.clicked.emit()
    assert(dialog.compType == 'one')
    assert(dialog.representationWidget.value() == 'mfcc')
    assert(dialog.distAlgWidget.value() == 'dtw')
    dialog.oneDirectoryWidget.pathEdit.setText('tests/data')
    kwargs = dialog.generateKwargs()
    assert(kwargs['type'] == 'one')
    assert(kwargs['rep'] == 'mfcc')
    assert(kwargs['match_func'] == 'dtw')
    assert(kwargs['num_filters'] == 26)
    assert(kwargs['num_coeffs'] == 12)
    assert(kwargs['freq_lims'] == (80, 7800))
    assert(kwargs['query'] == 'tests/data')

    dialog.twoDirectoryRadio.clicked.emit()
    assert(dialog.compType == 'two')
    dialog.directoryOneWidget.pathEdit.setText('tests/data')
    dialog.directoryTwoWidget.pathEdit.setText('tests/data')
    dialog.representationWidget.click(1)
    assert(dialog.representationWidget.value() == 'envelopes')
    dialog.distAlgWidget.click(1)
    assert(dialog.distAlgWidget.value() == 'xcorr')
    kwargs = dialog.generateKwargs()
    assert(kwargs['type'] == 'two')
    assert(kwargs['rep'] == 'envelopes')
    assert(kwargs['match_func'] == 'xcorr')
    assert(kwargs['num_filters'] == 8)
    assert(kwargs['freq_lims'] == (80, 7800))
    assert(kwargs['query'] == ['tests/data','tests/data'])

