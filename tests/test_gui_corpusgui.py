

from corpustools.gui.corpusgui import *
from PyQt5.QtTest import QTest


app = QApplication([])

def test_add_abstract_tier(specified_test_corpus):
    dialog = AddAbstractTierDialog(None,specified_test_corpus)

def test_add_column(specified_test_corpus):
    dialog = AddColumnDialog(None, specified_test_corpus)

def test_add_count_column(specified_test_corpus):
    dialog = AddCountColumnDialog(None, specified_test_corpus)


def test_add_tier(specified_test_corpus):
    dialog = AddTierDialog(None, specified_test_corpus)

def test_add_word(specified_test_corpus):
    dialog = AddWordDialog(None, specified_test_corpus)

def test_attribute_summary(specified_test_corpus):
    widget = AttributeSummary(specified_test_corpus)

def test_corpus_from_csv_dialog(settings):
    dialog = CorpusFromCsvDialog(None,settings)

def test_corpus_from_text_dialog(settings):
    dialog = CorpusFromTextDialog(None,settings)

def test_corpus_load_dialog(settings):
    dialog = CorpusLoadDialog(None, settings)

def test_corpus_select(settings):
    widget = CorpusSelect(None, settings)

def test_corpus_summary(specified_test_corpus):
    dialog = CorpusSummary(None, specified_test_corpus)

def test_corpus_download(settings):
    dialog = DownloadCorpusDialog(None, settings)

def test_corpus_export(specified_test_corpus):
    dialog = ExportCorpusDialog(None, specified_test_corpus)

def test_inventory_summary(specified_test_corpus):
    widget = InventorySummary(specified_test_corpus)

def test_remove_attribute(specified_test_corpus):
    dialog = RemoveAttributeDialog(None, specified_test_corpus)

def test_spontaneous_speech_import(settings):
    dialog = SpontaneousSpeechDialog(None, settings)

def test_subset_corpus(specified_test_corpus):
    dialog = SubsetCorpusDialog(None, specified_test_corpus)
