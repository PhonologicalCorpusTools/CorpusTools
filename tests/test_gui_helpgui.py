

from corpustools.gui.helpgui import *

def test_about_dialog(qtbot):
    dialog = AboutDialog(None)
    qtbot.addWidget(dialog)

def test_help_dialog(qtbot):
    dialog = HelpDialog(None)
    qtbot.addWidget(dialog)
