
from corpustools.gui.asgui import ASDialog

def test_asgui(qtbot):
    dialog = ASDialog(None, True)
    qtbot.addWidget(dialog)
