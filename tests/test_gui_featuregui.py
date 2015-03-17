
from corpustools.gui.featuregui import *

def test_feature_system_select(settings):
    widget = FeatureSystemSelect(settings, None)


def test_add_feature(spe_specifier):
    dialog = AddFeatureDialog(None, spe_specifier)

def test_download_feature_matrix(settings):
    dialog = DownloadFeatureMatrixDialog(None, settings)

def test_edit_feature_matrix(specified_test_corpus, settings):
    dialog = EditFeatureMatrixDialog(None, specified_test_corpus, settings)

def test_edit_segment(spe_specifier):
    dialog = EditSegmentDialog(None, spe_specifier)

def test_export_feature_matrix(specified_test_corpus):
    dialog = ExportFeatureSystemDialog(None, specified_test_corpus)

def test_feature_matrix_manager(settings):
    dialog = FeatureMatrixManager(None, settings)

def test_system_from_csv(settings):
    dialog = SystemFromCsvDialog(None, settings)
