

from corpustools.gui.migui import *

def test_migui(qtbot, specified_test_corpus):
    dialog = MIDialog(None,specified_test_corpus, True)
    qtbot.addWidget(dialog)
