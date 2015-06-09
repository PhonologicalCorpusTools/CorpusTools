

from corpustools.gui.corpusgui import *
#from corpustools.gui.widgets import AddTierDialog


def test_add_abstract_tier(qtbot, specified_test_corpus):
    dialog = AddAbstractTierDialog(None,specified_test_corpus)
    qtbot.addWidget(dialog)

def test_add_column(qtbot, specified_test_corpus):
    dialog = AddColumnDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_add_count_column(qtbot, specified_test_corpus):
    dialog = AddCountColumnDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_add_tier(qtbot, specified_test_corpus):
    dialog = AddTierDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_add_word(qtbot, specified_test_corpus):
    dialog = AddWordDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_attribute_summary(qtbot, specified_test_corpus):
    widget = AttributeSummary(specified_test_corpus)
    qtbot.addWidget(widget)

def test_corpus_summary(qtbot, specified_test_corpus):
    dialog = CorpusSummary(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_inventory_summary(qtbot, specified_test_corpus):
    widget = InventorySummary(specified_test_corpus)
    qtbot.addWidget(widget)

def test_remove_attribute(qtbot, specified_test_corpus):
    dialog = RemoveAttributeDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)
