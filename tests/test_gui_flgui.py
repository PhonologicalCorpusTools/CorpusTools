
from corpustools.gui.flgui import *

def test_flgui(qtbot, specified_test_corpus, settings):
    dialog = FLDialog(None, settings,specified_test_corpus, True)
    qtbot.addWidget(dialog)
