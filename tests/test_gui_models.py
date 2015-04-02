
from corpustools.gui.models import *

def test_base_corpus_model(qtbot, specified_test_corpus, settings):
    model = BaseCorpusTableModel(specified_test_corpus, settings)
    qtbot.addWidget(model)
    model.sort(2,Qt.DescendingOrder)
    index = model.index(0,0)
    print(index.row(),index.column())
    assert(model.data(index, Qt.DisplayRole) == 'sasi')
    assert(model.headerData(0,Qt.Horizontal, Qt.DisplayRole) == 'Spelling')

def test_base_table_model(qtbot, settings):
    model = BaseTableModel(settings)
    qtbot.addWidget(model)

    model.columns = ['1','2']
    model.addRows([[1,'2'],[True,['1','2','3']],[False, 0.1111111111]])
    index = model.index(-1,-1)
    assert(model.data(index, Qt.DisplayRole) == None)
    index = model.index(0,0)
    assert(model.data(index, Qt.DisplayRole) == '1')
    index = model.index(0,1)
    assert(model.data(index, Qt.DisplayRole) == '2')
    index = model.index(1,0)
    assert(model.data(index, Qt.DisplayRole) == 'Yes')
    index = model.index(1,1)
    assert(model.data(index, Qt.DisplayRole) == '1, 2, 3')
    index = model.index(2,0)
    assert(model.data(index, Qt.DisplayRole) == 'No')
    index = model.index(2,1)
    assert(model.data(index, Qt.DisplayRole) == '0.11111')

def test_corpus_model(qtbot, specified_test_corpus, settings):
    model = CorpusModel(specified_test_corpus, settings)
    qtbot.addWidget(model)

#def test_discourse_model(qtbot):
    #model = DiscourseModel()
    #qtbot.addWidget(model)

def test_environment_model(qtbot):
    model = EnvironmentModel()
    qtbot.addWidget(model)

def test_feature_system_table_model(qtbot, spe_specifier):
    model = FeatureSystemTableModel(spe_specifier)
    qtbot.addWidget(model)

def test_feature_system_tree_model(qtbot, spe_specifier):
    model = FeatureSystemTreeModel(spe_specifier)
    qtbot.addWidget(model)

def test_filter_model(qtbot):
    model = FilterModel()
    qtbot.addWidget(model)

def test_segment_pair_model(qtbot):
    model = SegmentPairModel()
    qtbot.addWidget(model)

def test_variant_model(qtbot, unspecified_test_corpus):
    w = unspecified_test_corpus['atema']
    model = VariantModel(w)
    qtbot.addWidget(model)

#def test_spontaneous_speech_model(qtbot):
    #model = SpontaneousSpeechCorpusModel()
    #qtbot.addWidget(model)


