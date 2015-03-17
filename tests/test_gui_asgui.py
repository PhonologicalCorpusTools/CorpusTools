
from corpustools.gui.asgui import *

def test_asgui(qtbot):
    dialog = ASDialog(None, True)
    qtbot.addWidget(dialog)
