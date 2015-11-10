
import unittest
from collections import OrderedDict
from corpustools.gui.widgets import *

from corpustools.corpus.classes.lexicon import Attribute


def test_parsing_dialog(qtbot, transcription_annotation_type):
    dialog = ParsingDialog(None, transcription_annotation_type, 'tier')
    qtbot.addWidget(dialog)

    assert(dialog.transDelimiter() == '.')
    assert(dialog.ignored() == set())
    assert(dialog.morphDelimiters() == set())
    assert(dialog.digraphs() == [])
    assert(dialog.numberBehavior() == None)

def test_transcription_annotation_type_widget(qtbot, transcription_annotation_type):
    widget = AnnotationTypeWidget(transcription_annotation_type)
    qtbot.addWidget(widget)
    assert(widget.value() == transcription_annotation_type)

def test_spelling_annotation_type_widget(qtbot, spelling_annotation_type):
    widget = AnnotationTypeWidget(spelling_annotation_type)
    qtbot.addWidget(widget)
    assert(widget.value() == spelling_annotation_type)

def test_numeric_annotation_type_widget(qtbot, numeric_annotation_type):
    widget = AnnotationTypeWidget(numeric_annotation_type)
    qtbot.addWidget(widget)
    assert(widget.value() == numeric_annotation_type)

def test_digraph_widget(qtbot):
    widget = DigraphWidget()
    qtbot.addWidget(widget)
    assert(widget.value() == [])

def test_segment_select_widget(qtbot, specified_test_corpus):
    widget = SegmentSelectionWidget(specified_test_corpus.inventory)
    qtbot.addWidget(widget)

def test_segment_select_dialog(qtbot, specified_test_corpus):
    widget = SegmentSelectDialog(specified_test_corpus.inventory)
    qtbot.addWidget(widget)

def test_segment_pair_dialog(qtbot, specified_test_corpus):
    dialog = SegmentPairDialog(specified_test_corpus.inventory)
    qtbot.addWidget(dialog)

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

def test_directory_widget(qtbot):
    widget = DirectoryWidget()
    qtbot.addWidget(widget)

    widget.setPath('test')

    assert(widget.value() == 'test')

def test_punctuation_widget(qtbot):
    widget = PunctuationWidget(['.',',','-'])
    qtbot.addWidget(widget)

    # Test value

    bs = widget.btnGroup.buttons()
    bs[0].setChecked(True)

    assert(widget.value() == {'.'})

    # Test check all

    widget.checkAll.clicked.emit()

    assert(widget.value() == {'.',',','-'})

    # Test uncheck all

    widget.uncheckAll.clicked.emit()

    assert(widget.value() == set())

def test_tier_widget(qtbot, specified_test_corpus):
    # Test with spelling
    widget = TierWidget(specified_test_corpus, include_spelling = True)
    qtbot.addWidget(widget)

    widget.tierSelect.setCurrentIndex(0)

    assert(widget.value() == 'spelling')
    assert(widget.displayValue() == 'Spelling')

    widget.tierSelect.setCurrentIndex(1)

    assert(widget.value() == 'transcription')
    assert(widget.displayValue() == 'Transcription')

    #Test disable spelling

    widget.setSpellingEnabled(False)

    widget.tierSelect.setCurrentIndex(0)

    assert(widget.value() == 'transcription')
    assert(widget.displayValue() == 'Transcription')

    # Test without spelling
    widget = TierWidget(specified_test_corpus, include_spelling = False)
    qtbot.addWidget(widget)

    widget.tierSelect.setCurrentIndex(0)

    assert(widget.value() == 'transcription')
    assert(widget.displayValue() == 'Transcription')

def test_radio_select_widget(qtbot):
    widget = RadioSelectWidget('', OrderedDict([('Option 1', 'option1'),('Option 2', 'option2')]))
    qtbot.addWidget(widget)
    widget.initialClick()

    assert(widget.value() == 'option1')
    assert(widget.displayValue() == 'Option 1')

    widget.disable()
    assert(not widget.widgets[0].isEnabled())

    widget.enable()
    assert(widget.widgets[0].isEnabled())


def test_inventory_box(qtbot, specified_test_corpus):
    widget = InventoryBox('Inventory', specified_test_corpus)
    qtbot.addWidget(widget)

    widget.setExclusive(True)
    bs = widget.btnGroup.buttons()
    for b in bs:
        b.setChecked(True)
    assert(widget.value() == bs[-1].text())

    widget.clearAll()

    assert(widget.value() == '')

    widget.setExclusive(False)
    assert(widget.value() == ())
    for b in widget.btnGroup.buttons():
        b.setChecked(True)

    assert(set(widget.value()) == set([ x.symbol for x in specified_test_corpus.inventory]))

def test_transcription_widget(qtbot, specified_test_corpus):
    widget = TranscriptionWidget('Transcription', specified_test_corpus)
    qtbot.addWidget(widget)

    widget.setText('test')

    assert(widget.text(), 'test')

    widget.setText('')
    expected = []
    for b in widget.segments.btnGroup.buttons():
        b.clicked.emit()
        expected.append(b.text())


    assert(widget.text() == '.'.join(expected))

def test_digraph_dialog(qtbot):
    dialog = DigraphDialog(['a','b','c'])
    qtbot.addWidget(dialog)

    # Test init

    b = dialog.buttons[0]
    assert(b.text() == 'a')

    # Test character adding

    b.clicked.emit()
    assert(dialog.value() == 'a')

    # Test duplicates okay

    b.clicked.emit()
    assert(dialog.value() == 'aa')

def test_segment_pair_widget(qtbot, specified_test_corpus):
    widget = SegmentPairSelectWidget(specified_test_corpus)
    qtbot.addWidget(widget)

    assert(widget.value() == [])

    widget.addPairs([('a','b')])
    assert(widget.value() == [('a','b')])

    widget.removePair()
    assert(widget.value() == [('a','b')])

    index = widget.table.model().createIndex(0,2)
    widget.table.itemDelegate(index).click(index)
    assert(widget.value() == [('b','a')])

    widget.table.selectionModel().select(
                widget.table.model().createIndex(0,0),
                QItemSelectionModel.Select|QItemSelectionModel.Rows)

    widget.removePair()
    assert(widget.value() == [])

def test_environment_select_widget(qtbot, specified_test_corpus):
    widget = EnvironmentSelectWidget(specified_test_corpus.inventory)

def test_environment_widget(qtbot, specified_test_corpus):
    widget = EnvironmentWidget(specified_test_corpus.inventory)

def test_environment_segment_widget(qtbot, specified_test_corpus):
    widget = EnvironmentSegmentWidget(specified_test_corpus.inventory)


def test_bigram_dialog(qtbot, specified_test_corpus, unspecified_test_corpus):

    # Test without _features
    widget = BigramWidget(specified_test_corpus.inventory)
    qtbot.addWidget(widget)
    dialog = BigramDialog(specified_test_corpus.inventory, widget)
    qtbot.addWidget(dialog)

    b1 = dialog.lhs.inventoryFrame.btnGroup.buttons()[0]
    b1.setChecked(True)
    b2 = dialog.rhs.inventoryFrame.btnGroup.buttons()[0]
    b2.setChecked(True)

    dialog.accept()
    #assert(dialog.env == '{}{}'.format(b1.text(),b2.text()))

def test_bigram_widget(qtbot, specified_test_corpus):
    widget = BigramWidget(specified_test_corpus.inventory)
    qtbot.addWidget(widget)

    assert(widget.value() == [])

    widget.table.model().addRow(['_a'])

    assert(widget.value() == ['_a'])

    widget.table.selectionModel().select(
                widget.table.model().createIndex(0,0),
                QItemSelectionModel.Select|QItemSelectionModel.Rows)

    widget.removeEnv()

    assert(widget.value() == [])


def test_factor_filter(qtbot):
    a = Attribute('name','factor','name')
    a.update_range('a')
    a.update_range('b')

    widget = FactorFilter(a)
    qtbot.addWidget(widget)

    assert(widget.value() == set())

    assert(widget.sourceWidget.item(0).text() == 'a')
    widget.sourceWidget.setCurrentRow(0)
    widget.addOneButton.clicked.emit()

    assert(widget.sourceWidget.item(0).text() == 'b')
    assert(widget.targetWidget.item(0).text() == 'a')
    assert(widget.value() == set(['a']))

    widget.clearAllButton.clicked.emit()
    assert(widget.sourceWidget.item(1).text() == 'a')
    assert(widget.targetWidget.count() == 0)
    assert(widget.sourceWidget.count() == 2)
    assert(widget.value() == set())

    widget.addAllButton.clicked.emit()
    assert(widget.sourceWidget.count() == 0)
    assert(widget.targetWidget.count() == 2)
    assert(widget.targetWidget.item(0).text() == 'b')
    assert(widget.targetWidget.item(1).text() == 'a')
    assert(widget.value() == set(['a','b']))

    widget.targetWidget.setCurrentRow(0)

    widget.clearOneButton.clicked.emit()
    assert(widget.sourceWidget.count() == 1)
    assert(widget.targetWidget.count() == 1)
    assert(widget.sourceWidget.item(0).text() == 'b')
    assert(widget.targetWidget.item(0).text() == 'a')
    assert(widget.value() == set(['a']))

def test_numeric_filter(qtbot):
    a = Attribute('name','numeric','name')
    a.update_range(0)
    a.update_range(100)
    widget = NumericFilter()
    qtbot.addWidget(widget)

    widget.valueEdit.setText('50')
    assert(widget.value() == (widget.conditionals[0],'50'))

def test_attribute_filter_dialog(qtbot, unspecified_test_corpus):
    widget = AttributeFilterWidget(unspecified_test_corpus)
    qtbot.addWidget(widget)
    dialog = AttributeFilterDialog(unspecified_test_corpus.attributes,widget)
    qtbot.addWidget(dialog)

    assert(isinstance(dialog.filterWidget, NumericFilter))

    dialog.filterWidget.valueEdit.setText('50')
    dialog.accept()
    assert(dialog.filter == (unspecified_test_corpus.attributes[2],operator.eq,50))



def test_corpus_select(qtbot, settings):
    widget = CorpusSelect(None, settings)
    qtbot.addWidget(widget)

    assert(widget.value() == '')
    assert(widget.path() is None)
