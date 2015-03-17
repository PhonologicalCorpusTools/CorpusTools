
from corpustools.gui.klgui import *

def test_klgui(qtbot, specified_test_corpus):
    dialog = KLDialog(None,specified_test_corpus, True)
    qtbot.addWidget(dialog)
