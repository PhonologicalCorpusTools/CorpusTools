

from corpustools.gui.psgui import *

def test_psgui(qtbot, specified_test_corpus):
    dialog = PhonoSearchDialog(None, specified_test_corpus, True)
    qtbot.addWidget(dialog)
