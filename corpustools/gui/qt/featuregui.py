import os
import copy

from .imports import *

from collections import OrderedDict
import codecs

from corpustools.config import config

from corpustools.corpus.io import (load_binary, download_binary,
                    load_feature_matrix_csv, save_binary, DelimiterError,
                    export_feature_matrix_csv)

from .views import TableWidget

from .models import FeatureSystemModel

from .widgets import FileWidget, RadioSelectWidget,SaveFileWidget

def get_systems_list():
    system_dir = os.path.join(config['storage']['directory'],'FEATURE')
    systems = [x.split('.')[0] for x in os.listdir(system_dir)]
    return systems

def system_name_to_path(name):
    return os.path.join(config['storage']['directory'],'FEATURE',name+'.feature')

class FeatureSystemSelect(QComboBox):
    def __init__(self,parent=None,default = None):
        QComboBox.__init__(self,parent)

        self.addItem('')
        for i,s in enumerate(get_systems_list()):
            self.addItem(s)
            if default is not None and s == default:
                self.setCurrentIndex(i+1)

    def value(self):
        return self.currentText()

    def path(self):
        if self.value() != '':
            return system_name_to_path(self.value())
        return None

class ExportFeatureSystemDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.specifier = corpus.specifier
        layout = QVBoxLayout()

        inlayout = QFormLayout()

        self.pathWidget = SaveFileWidget('Select file location','Text files (*.txt *.csv)')

        inlayout.addRow('File name:',self.pathWidget)

        self.columnDelimiterEdit = QLineEdit()
        self.columnDelimiterEdit.setText(',')

        inlayout.addRow('Column delimiter:',self.columnDelimiterEdit)

        inframe = QFrame()
        inframe.setLayout(inlayout)

        layout.addWidget(inframe)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Export feature system')

    def accept(self):
        filename = self.pathWidget.value()

        if filename == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a path to save the corpus.")
            return

        colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
        if len(colDelim) != 1:
            reply = QMessageBox.critical(self,
                    "Invalid information", "The column delimiter must be a single character.")
            return

        export_feature_matrix_csv(self.specifier,filename,colDelim)

        QDialog.accept(self)

class AddFeatureDialog(QDialog):
    def __init__(self, parent, specifier):
        QDialog.__init__(self, parent)
        self.specifier = specifier
        layout = QVBoxLayout()

        featureLayout = QFormLayout()
        self.featureEdit = QLineEdit()
        featureLayout.addRow('Feature name',self.featureEdit)

        featureFrame = QFrame()
        featureFrame.setLayout(featureLayout)

        layout.addWidget(featureFrame)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Add feature')

    def accept(self):
        self.featureName = self.featureEdit.text()
        if self.featureName == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a feature name.")
            return
        if self.featureName in self.specifier.features:
            reply = QMessageBox.critical(self,
                    "Duplicate information", "The feature '{}' is already in the feature system.".format(self.featureName))
            return
        QDialog.accept(self)

class DownloadFeatureMatrixDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()
        inlayout = QHBoxLayout()

        self.transWidget = RadioSelectWidget('Select a transcription system',
                                            OrderedDict([('IPA','ipa'),
                                                        ('ARPABET','arpa'),
                                                        ('XSAMPA','sampa'),
                                                        ('CELEX','celex'),
                                                        ('DISC','disc'),
                                                        ('Klatt','klatt')]))

        self.featureWidget = RadioSelectWidget('Select a feature system',
                                        OrderedDict([('Sound Pattern of English (SPE)','spe'),
                                        ('Hayes','hayes')]))

        inlayout.addWidget(self.transWidget)
        inlayout.addWidget(self.featureWidget)

        inframe = QFrame()
        inframe.setLayout(inlayout)

        layout.addWidget(inframe)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Download feature system')

class EditFeatureMatrixDialog(QDialog):
    def __init__(self, parent, corpus):
        QDialog.__init__(self, parent)

        self.corpus = corpus

        self.specifier = copy.deepcopy(self.corpus.specifier)

        layout = QVBoxLayout()

        self.table = TableWidget()
        self.table.setModel(FeatureSystemModel(self.specifier))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        optionLayout = QHBoxLayout()

        changeFrame = QGroupBox('Change feature systems')
        box = QFormLayout()
        self.changeWidget = FeatureSystemSelect(default=self.specifier.name)
        self.changeWidget.currentIndexChanged.connect(self.changeFeatureSystem)
        box.addRow(self.changeWidget)

        changeFrame.setLayout(box)

        optionLayout.addWidget(changeFrame)

        modifyFrame = QGroupBox('Modify the feature system')

        box = QFormLayout()

        self.addSegmentButton = QPushButton('Add segment')
        self.editSegmentButton = QPushButton('Edit segment')
        self.addFeatureButton = QPushButton('Add feature')
        self.addSegmentButton.clicked.connect(self.addSegment)
        self.editSegmentButton.clicked.connect(self.editSegment)
        self.addFeatureButton.clicked.connect(self.addFeature)

        box.addRow(self.addSegmentButton)
        box.addRow(self.editSegmentButton)
        box.addRow(self.addFeatureButton)

        modifyFrame.setLayout(box)

        optionLayout.addWidget(modifyFrame)

        coverageFrame = QGroupBox('Corpus inventory coverage')
        box = QFormLayout()

        self.hideButton = QPushButton('Hide all segments not used by the corpus')
        self.showAllButton = QPushButton('Show all segments')
        self.coverageButton = QPushButton('Check corpus inventory coverage')
        self.hideButton.clicked.connect(self.hide)
        self.showAllButton.clicked.connect(self.showAll)
        self.coverageButton.clicked.connect(self.checkCoverage)

        box.addRow(self.hideButton)
        box.addRow(self.showAllButton)
        box.addRow(self.coverageButton)

        coverageFrame.setLayout(box)

        optionLayout.addWidget(coverageFrame)

        optionFrame = QFrame()

        optionFrame.setLayout(optionLayout)

        layout.addWidget(optionFrame)

        self.acceptButton = QPushButton('Save changes to this corpus\'s feature system')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Edit feature system')

    def changeFeatureSystem(self):
        path = self.changeWidget.path()
        if path is None:
            self.specifier = None
        else:
            self.specifier = load_binary(path)
        self.table.setModel(FeatureSystemModel(self.specifier))

    def addSegment(self):
        dialog = EditSegmentDialog(self,self.table.model().specifier)
        if dialog.exec_():
            self.table.model().addSegment(dialog.seg,dialog.featspec)

    def editSegment(self):
        selected = self.table.selectionModel().selectedRows()[0]
        if not selected:
            return
        seg = self.table.model().data[selected.row()][0]
        dialog = EditSegmentDialog(self,self.table.model().specifier,seg)
        if dialog.exec_():
            self.table.model().addSegment(dialog.seg,dialog.featspec)

    def addFeature(self):
        dialog = AddFeatureDialog(self,self.table.model().specifier)
        if dialog.exec_():
            self.table.model().addFeature(dialog.featureName)

    def hide(self):
        self.table.model().filter(self.corpus.inventory)

    def showAll(self):
        self.table.model().showAll()

    def checkCoverage(self):
        corpus_inventory = self.corpus.inventory
        feature_inventory = self.specifier.segments
        missing = []
        for seg in corpus_inventory:
            if seg not in feature_inventory:
                missing.append(str(seg))
        if missing:
            reply = QMessageBox.warning(self,
                    "Missing segments", ', '.join(missing))
            return
        reply = QMessageBox.information(self,
                    "Missing segments", 'All segments are specified for features!')

class EditSegmentDialog(QDialog):
    def __init__(self, parent, specifier, segment = None):
        QDialog.__init__(self, parent)

        self.specifier = specifier
        layout = QVBoxLayout()

        featLayout = QGridLayout()
        self.symbolEdit = QLineEdit()
        self.add = True
        if segment is not None:
            self.add = False
            self.symbolEdit.setText(segment)
        box = QGroupBox('Symbol')
        lay = QVBoxLayout()
        lay.addWidget(self.symbolEdit)
        box.setLayout(lay)
        featLayout.addWidget(box,0,0)
        row = 0
        col = 1
        self.featureSelects = dict()
        for f in specifier.features:
            box = QGroupBox(f)
            lay = QVBoxLayout()

            featSel = QComboBox()
            for i,v in enumerate(specifier.possible_values):
                featSel.addItem(v)
                if segment is not None and v == specifier[segment][f]:
                    featSel.setCurrentIndex(i)
                elif v == specifier.default_value:
                    featSel.setCurrentIndex(i)
            lay.addWidget(featSel)
            box.setLayout(lay)
            self.featureSelects[f] = featSel
            featLayout.addWidget(box,row,col)

            col += 1
            if col > 11:
                col = 0
                row += 1

        featBox = QFrame()
        featBox.setLayout(featLayout)
        layout.addWidget(featBox)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Edit segment')

    def accept(self):
        self.seg = self.symbolEdit.text()
        if self.seg == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a segment symbol.")
            return
        if self.seg in self.specifier and self.add:
            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate symbol",
                    "The symbol '{}' already exists.  Overwrite?".format(self.seg), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Abort", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        self.featspec = {f:v.currentText() for f,v in self.featureSelects.items()}
        QDialog.accept(self)


class FeatureMatrixManager(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        formLayout = QHBoxLayout()
        listFrame = QGroupBox('Available feature systems')
        listLayout = QGridLayout()

        self.systemsList = QListWidget(self)
        listLayout.addWidget(self.systemsList)
        listFrame.setLayout(listLayout)
        self.getAvailableSystems()

        formLayout.addWidget(listFrame)

        buttonLayout = QVBoxLayout()
        self.downloadButton = QPushButton('Download feature systems')
        self.loadFromCsvButton = QPushButton('Create feature system from text file')
        self.removeButton = QPushButton('Remove selected feature system')
        buttonLayout.addWidget(self.downloadButton)
        buttonLayout.addWidget(self.loadFromCsvButton)
        buttonLayout.addWidget(self.removeButton)

        self.downloadButton.clicked.connect(self.openDownloadWindow)
        self.loadFromCsvButton.clicked.connect(self.openCsvWindow)
        self.removeButton.clicked.connect(self.removeSystem)

        buttonFrame = QFrame()
        buttonFrame.setLayout(buttonLayout)

        formLayout.addWidget(buttonFrame)

        formFrame = QFrame()
        formFrame.setLayout(formLayout)
        layout.addWidget(formFrame)

        self.acceptButton = QPushButton('Done')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        self.acceptButton.clicked.connect(self.accept)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Manage feature systems')

    def openCsvWindow(self):
        dialog = SystemFromCsvDialog(self)
        result = dialog.exec_()
        if result:
            self.getAvailableSystems()

    def openDownloadWindow(self):
        dialog = DownloadFeatureMatrixDialog(self)
        result = dialog.exec_()
        if result:
            self.getAvailableSystems()

    def removeSystem(self):
        featureSystem = self.systemsList.currentItem().text()
        msgBox = QMessageBox(QMessageBox.Warning, "Remove system",
                "This will permanently remove '{}'.  Are you sure?".format(featureSystem), QMessageBox.NoButton, self)
        msgBox.addButton("Remove", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return
        os.remove(system_name_to_path(featureSystem))
        self.getAvailableSystems()


    def getAvailableSystems(self):
        self.systemsList.clear()
        systems = get_systems_list()
        for s in systems:
            self.systemsList.addItem(s)

class SystemFromCsvDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

        formLayout = QFormLayout()


        self.pathWidget = FileWidget('Open corpus csv','Text files (*.txt *.csv)')
        self.pathWidget.textChanged.connect(self.updateName)

        formLayout.addRow(QLabel('Path to feature system'),self.pathWidget)

        self.nameEdit = QLineEdit()
        formLayout.addRow(QLabel('Name for feature system (auto-suggested)'),self.nameEdit)

        self.columnDelimiterEdit = QLineEdit()
        self.columnDelimiterEdit.setText(',')
        formLayout.addRow(QLabel('Column delimiter (enter \'\\t\' for tab)'),self.columnDelimiterEdit)

        formFrame = QFrame()
        formFrame.setLayout(formLayout)
        layout.addWidget(formFrame)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Create feature system from csv')

    def updateName(self):
        self.nameEdit.setText(os.path.split(self.pathWidget.value())[1].split('.')[0])

    def accept(self):
        path = self.pathWidget.value()
        if not os.path.exists(path):
            dialog = QMessageBox()
            dialog.setText('Feature matrix file could not be located. Please verify the path and file name.')
            dialog.exec_()
            return

        name = self.nameEdit.text()
        colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
        if (not path) or (not colDelim) or (not name):
            MessageBox.showerror(message='Information is missing. Please verify that you entered something in all the text boxes')
            return
        try:
            system = load_feature_matrix_csv(name, path, colDelim)
        except DelimiterError:
            dialog = QMessageBox()
            dialog.setText('Could not parse the file.\nCheck that the delimiter you typed in matches the one used in the file.')
            dialog.exec_()
            return
        except KeyError:
            dialog = QMessageBox()
            dialog.setText('Could not find a \'symbol\' column.  Please make sure that the segment symbols are in a column named \'symbol\'.')
            dialog.exec_()
            return
        save_binary(system,system_name_to_path(name))

        QDialog.accept(self)
