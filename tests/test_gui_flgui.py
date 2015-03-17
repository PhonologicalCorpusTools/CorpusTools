
from corpustools.gui.flgui import *

def test_flgui(qtbot, specified_test_corpus):
    dialog = FLDialog(None,specified_test_corpus, True)
    qtbot.addWidget(dialog)
