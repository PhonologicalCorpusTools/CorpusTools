
from corpustools.gui.models import *
from corpustools.corpus.classes import Word, Attribute

def test_base_corpus_model(qtbot, specified_test_corpus, settings):
    model = BaseCorpusTableModel(specified_test_corpus, settings)
    model.sort(2,Qt.DescendingOrder)
    index = model.index(0,0)
    print(index.row(),index.column())
    assert(model.data(index, Qt.DisplayRole) == 'sasi')
    assert(model.headerData(0,Qt.Horizontal, Qt.DisplayRole) == 'Spelling')

def test_base_table_model(qtbot, settings):
    model = BaseTableModel(settings)

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
    assert(model.data(index, Qt.DisplayRole) == '0.111')

def test_corpus_model(qtbot, specified_test_corpus, settings):
    model = CorpusModel(specified_test_corpus, settings)
    assert(model.headerData(0,Qt.Horizontal,Qt.DisplayRole) == 'Spelling')
    assert(model.headerData(1,Qt.Horizontal,Qt.DisplayRole) == 'Transcription')
    assert(model.headerData(2,Qt.Horizontal,Qt.DisplayRole) == 'Frequency')

    a = Attribute('test', 'spelling','Test2')

    model.addColumn(a)
    assert(model.headerData(3,Qt.Horizontal,Qt.DisplayRole) == 'Test2')

    model.removeAttributes(['Test2'])
    assert(len(model.columns) == 3)

    a = Attribute('test','factor','Test')

    model.addAbstractTier(a, {'C':['t','m']})
    assert(model.wordObject(0).test == 'CC')
    model.removeAttributes(['Test'])

    a = Attribute('test','numeric','Test')

    model.addCountColumn(a, 'transcription', ['t','m'])
    assert(model.wordObject(0).test == 2)
    model.removeAttributes(['Test'])

    a = Attribute('test','tier','Test')

    model.addTier(a, ['t','m'])
    assert(model.wordObject(0).test == ['t','m'])
    model.removeAttributes(['Test'])

    w = model.wordObject(0)
    assert(w.spelling == 'atema')
    w = Word(spelling = 'atema', transcription = [])
    model.replaceWord(0, w)
    w = model.wordObject(0)
    assert(w.spelling == 'atema' and w.transcription == [])
    model.hideNonLexical(True)
    w = model.wordObject(0)
    assert(w.spelling != 'atema')
    model.hideNonLexical(False)
    w = model.wordObject(0)
    assert(w.spelling == 'atema')


#def test_discourse_model(qtbot):
    #model = DiscourseModel()

def test_environment_model(qtbot):
    model = EnvironmentModel()

def test_feature_system_table_model(qtbot, spe_specifier):
    model = FeatureSystemTableModel(spe_specifier)

def test_feature_system_tree_model(qtbot, spe_specifier):
    model = FeatureSystemTreeModel(spe_specifier)

def test_filter_model(qtbot):
    model = FilterModel()
    a = Attribute('test','numeric','Test')
    f = (a, '__eq__', 0)
    model.addRow(f)
    assert(model.data(model.index(0,0),Qt.DisplayRole) == 'Test == 0')

    model.removeRow(0)

    assert(len(model.filters) == 0)

    a = Attribute('test','factor','Test')
    f = (a, ['a','b','c'])
    model.addRow(f)
    assert(model.data(model.index(0,0),Qt.DisplayRole) == 'Test a, b, c')

def test_segment_pair_model(qtbot):
    model = SegmentPairModel()

def test_variant_model(qtbot, unspecified_test_corpus):
    w = unspecified_test_corpus['atema']
    model = VariantModel(w)

def test_results_model(qtbot, settings):
    model = ResultsModel([], [], settings)

def test_phono_search_results_model(qtbot, unspecified_test_corpus, settings):
    model = PhonoSearchResultsModel([],[],[], settings)

#def test_spontaneous_speech_model(qtbot):
    #model = SpontaneousSpeechCorpusModel()


