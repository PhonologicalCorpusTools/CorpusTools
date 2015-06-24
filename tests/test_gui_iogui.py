

from corpustools.gui.iogui import *

def test_import_corpus_dialog(qtbot, settings):
    dialog = LoadCorpusDialog(None,settings)
    qtbot.addWidget(dialog)

def test_corpus_load_dialog(qtbot, settings):
    dialog = CorpusLoadDialog(None, settings)
    qtbot.addWidget(dialog)

def test_corpus_download(qtbot, settings):
    dialog = DownloadCorpusDialog(None, settings)
    qtbot.addWidget(dialog)

def test_corpus_export(qtbot, specified_test_corpus):
    dialog = ExportCorpusDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_subset_corpus(qtbot, specified_test_corpus):
    dialog = SubsetCorpusDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)
