
from corpustools.gui.windows import *

#def test_pctdialog(qtbot):
#    dialog = FunctionDialog()
    #qtbot.addWidget(dialog)

def test_progress_dialog(qtbot):
    dialog = ProgressDialog(None)
    qtbot.addWidget(dialog)


    dialog.updateText('testing!')
    assert(dialog.labelText() == 'testing!\nTime left: Unknown')


    dialog.updateProgress(0)
    assert(dialog.startTime is not None)
    dialog.updateProgress(0.1)
    assert(len(dialog.rates) == 1)

    dialog.cancel()
    assert(dialog.labelText() == 'Canceling...')
    assert(not dialog.cancelButton.isEnabled())

    dialog.reject()
