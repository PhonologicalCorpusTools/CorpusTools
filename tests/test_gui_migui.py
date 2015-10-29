

from corpustools.gui.migui import *

def test_migui(qtbot, specified_test_corpus, settings):
    dialog = MIDialog(None, settings,specified_test_corpus, True)
    qtbot.addWidget(dialog)
