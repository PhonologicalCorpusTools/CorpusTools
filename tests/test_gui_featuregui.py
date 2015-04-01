
from corpustools.gui.featuregui import *


def test_feature_system_select(qtbot, settings):
    widget = FeatureSystemSelect(settings, None)
    qtbot.addWidget(widget)


def test_add_feature(qtbot, spe_specifier):
    dialog = AddFeatureDialog(None, spe_specifier)
    qtbot.addWidget(dialog)

def test_download_feature_matrix(qtbot, settings):
    dialog = DownloadFeatureMatrixDialog(None, settings)
    qtbot.addWidget(dialog)

def test_edit_feature_matrix(qtbot, specified_test_corpus, settings):
    dialog = EditFeatureMatrixDialog(None, specified_test_corpus, settings)
    qtbot.addWidget(dialog)

def test_edit_segment(qtbot, spe_specifier):
    dialog = EditSegmentDialog(None, spe_specifier)
    qtbot.addWidget(dialog)

def test_export_feature_matrix(qtbot, specified_test_corpus):
    dialog = ExportFeatureSystemDialog(None, specified_test_corpus)
    qtbot.addWidget(dialog)

def test_feature_matrix_manager(qtbot, settings):
    dialog = FeatureMatrixManager(None, settings)
    qtbot.addWidget(dialog)

def test_system_from_csv(qtbot, settings):
    dialog = SystemFromCsvDialog(None, settings)
    qtbot.addWidget(dialog)
