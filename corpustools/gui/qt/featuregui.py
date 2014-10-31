import os

from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox, QMessageBox)

from collections import OrderedDict
import codecs

from corpustools.config import config

from corpustools.corpus.io import (load_binary, download_binary,
                    load_feature_matrix_csv, save_binary, DelimiterError)

from .widgets import FileWidget, RadioSelectWidget

def get_systems_list():
    system_dir = os.path.join(config['storage']['directory'],'FEATURE')
    systems = [x.split('.')[0] for x in os.listdir(system_dir)]
    return systems

def system_name_to_path(name):
    return os.path.join(config['storage']['directory'],'FEATURE',name+'.feature')

class AddFeatureDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

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
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

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

        self.setWindowTitle('View feature system')

class EditSegmentDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()

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

        self.setWindowTitle('Load corpora')

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
        pass

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
