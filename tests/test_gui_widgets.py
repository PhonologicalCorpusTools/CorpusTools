
import unittest
from collections import OrderedDict
from corpustools.gui.widgets import *

from corpustools.corpus.classes.lexicon import Attribute


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

    assert(widget.value() == ['.'])

    # Test check all

    widget.checkAll.clicked.emit()

    assert(widget.value() == ['.',',','-'])

    # Test uncheck all

    widget.uncheckAll.clicked.emit()

    assert(widget.value() == [])

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
    assert(widget.value() == [])
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

def test_feature_box(qtbot, specified_test_corpus):
    widget = FeatureBox('Transcription', specified_test_corpus.inventory)
    qtbot.addWidget(widget)

    # Test basic init

    assert(set(widget.features) == set(['EXTRA','LONG','ant','back','cont','cor',
                'del_rel','distr','glot_cl','hi_subgl_pr','high',
                'lat','low','mv_glot_cl','nasal','round','son',
                'strid','tense','voc','voice']))

    assert(set(widget.values) == set(['n','+','-','.']))

    f, v = widget.features[0], widget.values[0]
    f2, v2 = widget.features[1], widget.values[1]

    # Test default return value

    assert(widget.value() == '')

    # Test no action when no features selected

    b = widget.buttons[0]
    b.clicked.emit()
    assert(widget.value() == '')

    # Test single feature selected

    widget.featureList.setCurrentRow(0)
    b.clicked.emit()
    assert(widget.value() == '[{}{}]'.format(v,f))

    # Test multiple features selected

    widget.featureList.setCurrentRow(1)
    b2 = widget.buttons[1]
    b2.clicked.emit()
    assert(widget.value() == '[{}{},{}{}]'.format(v,f,v2,f2))

    # Test to ensure values are unique

    b2.clicked.emit()
    assert(widget.value() == '[{}{},{}{}]'.format(v,f,v2,f2))

    # Test clear all

    widget.clearButton.clicked.emit()
    assert(widget.value() == '')

    widget.featureList.setCurrentRow(0)
    b.clicked.emit()

    widget.featureList.setCurrentRow(1)
    b2.clicked.emit()

    widget.envList.setCurrentRow(0)
    widget.clearOneButton.clicked.emit()
    assert(widget.value() == '[{}{}]'.format(v2,f2))

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
    widget = EnvironmentSelectWidget(specified_test_corpus)
    qtbot.addWidget(widget)

    assert(widget.value() == [])

    widget.table.model().addRow(['_a'])

    assert(widget.value() == ['_a'])

    widget.table.selectionModel().select(
                widget.table.model().createIndex(0,0),
                QItemSelectionModel.Select|QItemSelectionModel.Rows)

    widget.removeEnv()

    assert(widget.value() == [])

def test_environment_dialog(qtbot, specified_test_corpus, unspecified_test_corpus):
    # Test with features
    widget = EnvironmentSelectWidget(specified_test_corpus)
    qtbot.addWidget(widget)
    dialog = EnvironmentDialog(specified_test_corpus, widget)
    qtbot.addWidget(dialog)

    assert(dialog.lhsEnvType.count() == 2)
    assert(dialog.rhsEnvType.count() == 2)

    assert(isinstance(dialog.lhs, InventoryBox))
    dialog.lhsEnvType.setCurrentIndex(1)
    assert(isinstance(dialog.lhs, FeatureBox))

    assert(isinstance(dialog.rhs, InventoryBox))
    dialog.rhsEnvType.setCurrentIndex(1)
    assert(isinstance(dialog.rhs, FeatureBox))

    f, v = dialog.rhs.features[0], dialog.rhs.values[0]
    dialog.rhs.featureList.setCurrentRow(0)
    b = dialog.rhs.buttons[0]
    b.clicked.emit()

    dialog.accept()
    assert(dialog.env == '_[{}{}]'.format(v,f))

    # Test without features
    widget = EnvironmentSelectWidget(unspecified_test_corpus.inventory)
    dialog = EnvironmentDialog(unspecified_test_corpus, widget)

    assert(dialog.lhsEnvType.count() == 1)
    assert(dialog.rhsEnvType.count() == 1)

    b = dialog.lhs.btnGroup.buttons()[0]
    b.setChecked(True)

    dialog.accept()
    assert(dialog.env == '{}_'.format(b.text()))

def test_bigram_dialog(qtbot, specified_test_corpus, unspecified_test_corpus):

    # Test without features
    widget = BigramWidget(specified_test_corpus.inventory)
    qtbot.addWidget(widget)
    dialog = EnvironmentDialog(specified_test_corpus, widget)
    qtbot.addWidget(dialog)

    b1 = dialog.lhs.btnGroup.buttons()[0]
    b1.setChecked(True)
    b2 = dialog.rhs.btnGroup.buttons()[0]
    b2.setChecked(True)

    dialog.accept()
    assert(dialog.env == '{}{}'.format(b1.text(),b2.text()))

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

def test_segfeat_select(qtbot, specified_test_corpus, unspecified_test_corpus):
    widget = SegFeatSelect(specified_test_corpus,'')
    qtbot.addWidget(widget)

    assert(widget.typeSelect.count() == 2)

    assert(isinstance(widget.sel, InventoryBox))
    widget.typeSelect.setCurrentIndex(1)
    assert(isinstance(widget.sel, FeatureBox))

    widget.sel.envList.addItem('+voc')

    assert(widget.value() == '[+voc]')

    assert(set(widget.segments()) == set(['ɑ','e','i','u','o']))

    widget = SegFeatSelect(unspecified_test_corpus,'')
    qtbot.addWidget(widget)

    assert(widget.typeSelect.count() == 1)

    b = widget.sel.btnGroup.buttons()[0]
    b.setChecked(True)

    assert(widget.value() == [b.text()])

    assert(widget.segments() == [b.text()])

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


