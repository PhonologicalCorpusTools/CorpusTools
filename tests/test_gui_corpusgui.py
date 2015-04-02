

from corpustools.gui.corpusgui import *

def test_attribute_widget(qtbot,specified_test_corpus):
    new = AttributeWidget()
    assert(new.nameWidget.isEnabled())
    new.nameWidget.setText('test')

    for i,v in enumerate(['Custom column', 'Spelling', 'Transcription', 'Frequency']):
        new.useAs.setCurrentIndex(i)
        att = new.value()
        if i == 0:
            assert(new.typeWidget.isEnabled())
            assert(att.name == 'test')
            assert(att.att_type == 'spelling')
        elif i == 1:
            assert(not new.typeWidget.isEnabled())
            assert(new.typeWidget.currentText() == 'Spelling')
            assert(att.name == 'spelling')
            assert(att.display_name == 'test')
            assert(att.att_type == 'spelling')
        elif i == 2:
            assert(not new.typeWidget.isEnabled())
            assert(new.typeWidget.currentText() == 'Tier')
            assert(att.name == 'transcription')
            assert(att.display_name == 'test')
            assert(att.att_type == 'tier')
        elif i == 3:
            assert(not new.typeWidget.isEnabled())
            assert(new.typeWidget.currentText() == 'Numeric')
            assert(att.name == 'frequency')
            assert(att.display_name == 'test')
            assert(att.att_type == 'numeric')

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

def test_corpus_from_csv_dialog(qtbot, settings):
    dialog = CorpusFromCsvDialog(None,settings)
    qtbot.addWidget(dialog)

def test_corpus_from_text_dialog(qtbot, settings):
    dialog = CorpusFromTextDialog(None,settings)
    qtbot.addWidget(dialog)

def test_corpus_load_dialog(qtbot, settings):
    dialog = CorpusLoadDialog(None, settings)
    qtbot.addWidget(dialog)

def test_corpus_select(qtbot, settings):
    widget = CorpusSelect(None, settings)
    qtbot.addWidget(widget)

def test_corpus_summary(qtbot, specified_test_corpus):
    dialog = CorpusSummary(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_corpus_download(qtbot, settings):
    dialog = DownloadCorpusDialog(None, settings)
    qtbot.addWidget(dialog)

def test_corpus_export(qtbot, specified_test_corpus):
    dialog = ExportCorpusDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_inventory_summary(qtbot, specified_test_corpus):
    widget = InventorySummary(specified_test_corpus)
    qtbot.addWidget(widget)

def test_remove_attribute(qtbot, specified_test_corpus):
    dialog = RemoveAttributeDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_spontaneous_speech_import(qtbot, settings):
    dialog = SpontaneousSpeechDialog(None, settings)
    qtbot.addWidget(dialog)

def test_subset_corpus(qtbot, specified_test_corpus):
    dialog = SubsetCorpusDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)
