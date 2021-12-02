import os
from collections import OrderedDict
import webbrowser
import codecs


from .imports import *
from corpustools.exceptions import PCTError, PCTPythonError

from corpustools.corpus.io import (load_binary, download_binary,
                    load_feature_matrix_csv, save_binary, DelimiterError,
                    export_feature_matrix_csv)

from corpustools.corpus.io.helper import punctuation_names

from .views import SubTreeView
from .models import FeatureSystemTableModel, FeatureSystemTreeModel

from .widgets import (FileWidget, RadioSelectWidget,SaveFileWidget,
                    TableWidget, RetranscribeWidget, FeatureEdit, FeatureCompleter, FileNameDialog)

from .windows import FunctionWorker, DownloadWorker, PCTDialog
from .helpgui import HelpDialog, get_url
import corpustools.gui.modernize as modernize
from urllib.request import urlretrieve

class LoadFeatureSystemWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        try:
            system = load_feature_matrix_csv(**self.kwargs)
        except PCTError as e:
            self.errorEncountered.emit(e)
            return
        except Exception as e:
            e = PCTPythonError(e)
            self.errorEncountered.emit(e)
            return
        if self.stopped:
            time.sleep(0.1)
            self.finishedCancelling.emit()
            return
        self.dataReady.emit(system)


def get_systems_list(storage_directory):
    system_dir = os.path.join(storage_directory,'FEATURE')
    systems = [x.split('.feature')[0] for x in os.listdir(system_dir) if x.endswith('.feature')]
    systems = sorted(systems, key=lambda s:s.lower())
    return systems

def get_feature_system_styles(storage_directory):
    systems = list()
    for s in get_systems_list(storage_directory):
        deets = s.split('2')
        if len(deets) == 1:
            continue
        systems.append(deets[1])
    return list(set(systems))

def get_transcription_system_styles(storage_directory):
    systems = list()
    for s in get_systems_list(storage_directory):
        deets = s.split('2')
        if len(deets) == 1:
            continue
        systems.append(deets[0])
    return list(set(systems))

def system_name_to_path(storage_directory,name):
    return os.path.join(storage_directory,'FEATURE',name+'.feature')

class FeatureSystemSelect(QGroupBox):
    changed  = Signal()
    def __init__(self, settings, parent=None, default = None, add = False):
        QGroupBox.__init__(self,'Transcription and features',parent)
        self.settings = settings
        layout = QFormLayout()

        self.transSystem = QComboBox()
        if add:
            self.transSystem.addItem('Custom')
        else:
            self.transSystem.addItem('None')
        if default is not None:
            default_deets = default.split('2')
            if len(default_deets) == 1:
                default_trans = 'None'
                default_feat = 'None'
            else:
                default_trans,default_feat = default_deets

        for i,s in enumerate(get_transcription_system_styles(self.settings['storage'])):
            self.transSystem.addItem(s)
            if default is not None and s == default_trans:
                self.transSystem.setCurrentIndex(i+1)
        self.transSystem.currentIndexChanged.connect(self.toggleTransName)
        layout.addRow(QLabel('Transcription system'),self.transSystem)

        self.transName = QLineEdit()
        if add:
            layout.addRow(QLabel('Transcription system name (if custom)'),self.transName)

        self.featureSystem = QComboBox()
        if add:
            self.featureSystem.addItem('Custom')
        else:
            self.featureSystem.addItem('None')
        for i,s in enumerate(get_feature_system_styles(self.settings['storage'])):
            self.featureSystem.addItem(s)
            if default is not None and s == default_feat:
                self.featureSystem.setCurrentIndex(i+1)
        self.featureSystem.currentIndexChanged.connect(self.toggleFeatName)
        layout.addRow(QLabel('Feature system'),self.featureSystem)

        self.featName = QLineEdit()
        if add:
            layout.addRow(QLabel('Feature system name (if custom)'),self.featName)

        self.setLayout(layout)

    def toggleTransName(self, ind = None):
        if self.transSystem.currentText() == 'Custom':
            self.transName.setDisabled(False)
        else:
            self.transName.setDisabled(True)
        self.changed.emit()

    def toggleFeatName(self, ind = None):
        if self.featureSystem.currentText() == 'Custom':
            self.featName.setDisabled(False)
        else:
            self.featName.setDisabled(True)
        self.changed.emit()

    def value(self):
        trans = self.transSystem.currentText()
        feat = self.featureSystem.currentText()
        if trans == 'None':
            return ''
        if feat == 'None':
            return ''
        if trans == 'Custom':
            trans = self.transName.text()
            if trans == '':
                return ''
        if feat == 'Custom':
            feat = self.featName.text()
            if feat == '':
                return ''
        return '2'.join([trans,feat])

    def path(self):
        if self.value() != '':
            return system_name_to_path(self.settings['storage'], self.value())
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

        # Success message
        QMessageBox.information(self, "Feature matrix exported",
                                f"You successfully exported the \'{self.specifier.name}\' feature.\n"
                                f"It is saved as \'{filename}.\'",
                                QMessageBox.Ok, QMessageBox.Ok)
        QDialog.accept(self)

        QDialog.accept(self)

class RestrictedFeatureSystemSelect(QGroupBox):

    def __init__(self, settings, specifier, parent=None):
        QGroupBox.__init__(self, 'Transcription and feature file', parent)
        self.settings = settings
        layout = QFormLayout()

        self.systems = QComboBox()
        self.systems.addItems(get_systems_list(settings['storage']))
        self.systems.addItem('None')
        if specifier is not None:
            self.systems.setCurrentText(specifier.name)

        layout.addWidget(self.systems)

        self.setLayout(layout)

    def path(self):
        name = self.systems.currentText()
        if name == 'None':
            return None
        return system_name_to_path(self.settings['storage'], name)

    def value(self):
        return self.systems.currentText()

class AddFeatureDialog(QDialog):
    def __init__(self, parent, specifier):
        QDialog.__init__(self, parent)
        self.specifier = specifier
        layout = QVBoxLayout()

        featureLayout = QFormLayout()
        self.featureEdit = QLineEdit()
        featureLayout.addRow('Feature name',self.featureEdit)
        self.defaultSelect = QComboBox()
        self.defaultSelect.addItem(specifier.default_value)
        for i,v in enumerate(specifier.possible_values):
            if v == specifier.default_value:
                continue
            self.defaultSelect.addItem(v)
        featureLayout.addRow('Default value for this feature:',self.defaultSelect)

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
        self.defaultValue = self.defaultSelect.currentText()
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
    def __init__(self, parent, settings):
        QDialog.__init__(self, parent)

        self.settings = settings
        layout = QVBoxLayout()
        inlayout = QHBoxLayout()

        self.transWidget = RadioSelectWidget('Select a transcription system',
                                            OrderedDict([('IPA','ipa'),
                                                        ('ARPABET (CMU)','arpabet'),
                                                        ('XSAMPA','sampa'),
                                                        ('CPA','cpa'),
                                                        ('CELEX','celex'),
                                                        ('DISC','disc'),
                                                        ('Klatt','klatt'),
                                                        ('Buckeye','buckeye')]))

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
        self.helpButton = QPushButton('Help')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.helpButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Download feature system')

        self.thread = DownloadWorker()

        self.progressDialog = QProgressDialog('Downloading...','Cancel',0,100,self)
        self.progressDialog.setWindowTitle('Download feature system')
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.finished.connect(self.progressDialog.accept)

    def help(self):
        url = get_url('transcriptions and feature systems',
                      section='downloadable-transcription-and-feature-choices')
        webbrowser.open(url)
        # self.helpDialog = HelpDialog(self,name = 'transcriptions and feature systems',
        #                             section = 'downloadable-transcription-and-feature-choices')
        # self.helpDialog.exec_()

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def accept(self):
        name = self.transWidget.value() + '2' + self.featureWidget.value()
        if name in get_systems_list(self.settings['storage']):
            msgBox = QMessageBox(QMessageBox.Warning, "Overwrite system",
                    "The system '{}' is already available.  Would you like to overwrite it?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return
        try:
            # try downloading a tiny bit from the PCT file storage on Dropbox.
            # If fails for whatever reason, including no internet or SSL-certi issue on MacOS, prompt an error message.
            # When making any changes to here, check the equivalent part on iogui.py as well.
            urlretrieve('https://www.dropbox.com/s/ytcl72nxydiqkyg/do_not_remove.txt?dl=1')
        except:
            QMessageBox.critical(self, 'Cannot access online repository',
                                 'PCT could not make a secured connection to PCT repository hosted at Dropbox.\n\n'
                                 'Please make sure you are connected to the internet. \nIf you are using MacOS, '
                                 'Go to "Applications -> Python x.y (your version)" on Finder and run '
                                 '"Certificates.command".')
            return

        self.thread.setParams({'name':name,
                'path':system_name_to_path(self.settings['storage'],name)})

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            QDialog.accept(self)

class EditFeatureMatrixDialog(QDialog):
    def __init__(self, parent, corpus, settings):
        QDialog.__init__(self, parent)
        self.corpus = corpus
        self.settings = settings
        self.specifier = self.corpus.specifier
        self.transcription_system = self.specifier.trans_name if self.specifier is not None else 'None'
        self.feature_system = self.specifier.feature_name if self.specifier is not None else 'None'
        self.feature_system_changed = False
        self.transcription_changed = False
        self.specs_changed = False
        self.segmap = dict()
        layout = QVBoxLayout()

        self.table = TableWidget()
        #self.table.setModel(FeatureSystemTableModel(self.specifier))
        #layout.addWidget(self.table)

        optionLayout = QHBoxLayout()

        changeFrame = QGroupBox('Change feature systems')
        box = QFormLayout()
        #self.changeWidget = FeatureSystemSelect(self.settings,default=default)
        self.changeWidget = RestrictedFeatureSystemSelect(self.settings, self.specifier)
        self.changeWidget.systems.currentIndexChanged.connect(self.changeRestrictedFeatureSystem)
        if self.specifier is not None:
            pos = self.changeWidget.systems.findText(self.specifier.name)
            self.changeWidget.systems.setCurrentIndex(pos)
        else:
            self.changeWidget.systems.setCurrentIndex(0)
        #self.changeWidget.transSystem.activated.connect(self.changeFeatureSystem)
        #self.changeWidget.featureSystem.activated.connect(self.changeFeatureSystem)

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


        viewFrame = QGroupBox('Display options')
        box = QFormLayout()

        self.displayWidget = QComboBox()
        self.displayWidget.addItem('Matrix')
        # THE TREE VIEW DOES NOT WORK (AS OF PCT v.1.2) SO IT IS BEING COMMENTED OUT, WITH THE HOPE OF REVIVING IT
        # SOME DAY IN THE FUTURE
        #self.displayWidget.addItem('Tree')
        self.displayWidget.currentIndexChanged.connect(self.changeDisplay)

        box.addRow('Display mode:',self.displayWidget)

        viewFrame.setLayout(box)

        optionLayout.addWidget(viewFrame)

        optionFrame = QFrame()

        optionFrame.setLayout(optionLayout)

        layout.addWidget(optionFrame)

        self.acceptButton = QPushButton('Save changes to this feature system')
        self.cancelButton = QPushButton('Cancel')
        self.helpButton = QPushButton('Help')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.helpButton)
        #self.acceptButton.clicked.connect(self.accept)
        self.acceptButton.clicked.connect(self.acceptRestricted)
        self.cancelButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Edit feature system')

        self.changeDisplay()

    def acceptRestricted(self):
        if self.specifier is None:
            QDialog.accept(self)
            return

        oldSystem = self.specifier.name
        missing = []
        feature_inventory = self.specifier.segments
        for seg in self.corpus.inventory:
            if seg not in feature_inventory:
                if seg == '\'':
                    missing.append('\' (apostrophe)')
                else:
                    missing.append(str(seg))
        if missing:
            missing = ','.join(missing)
            alert = QMessageBox()
            alert.setWindowTitle('Warning')
            alert.setText(('The following symbols in your corpus do not match up with any symbols in your '
                    'selected feature system:\n{}\n\n'
                'You should select a different feature system, or else use the "Add Segment" button to add these '
                'symbols to the current feature system'.format(missing)))
            alert.exec_()
            return

        if self.specs_changed and self.settings['ask_overwrite_features']:
            systems = get_systems_list(self.settings['storage'])
            if self.specifier.name in systems:
                try:
                    if self.corpus.name in self.specifier.name:
                        if len(self.specifier.name.split('-'))==1:
                            name_hint = self.specifier.name+'-2'
                        else:
                            name_hint = self.specifier.name[:-1]
                            name_hint += str(int(self.specifier.name[-1])+1)
                    else:
                        name_hint = '_'.join([self.specifier.name, self.corpus.name])
                except:
                    name_hint = self.specifier.name+'-new'

            fileNameDialog = FileNameDialog(self.specifier.name, 'features', self.settings, hint=name_hint)
            fileNameDialog.exec_()
            if fileNameDialog.choice == 'cancel':
                return
            elif fileNameDialog.choice == 'saveas':
                name = fileNameDialog.getFilename()
                if name.endswith('.feature'):
                    name.rstrip('.feature')
                self.specifier.name = name
            elif fileNameDialog.choice == 'overwrite':
                pass

            self.settings['ask_overwrite_features'] = int(not fileNameDialog.stopShowing.isChecked())


        self.transcription_changed = False
        self.feature_system_changed = False if self.specifier.name == oldSystem else True
        filename = os.path.join(self.settings['storage'], 'FEATURE', self.specifier.name)
        if not filename.endswith('.feature'):
            filename += '.feature'
        save_binary(self.specifier, filename)
        QDialog.accept(self)


    def accept(self):
        info = self.changeWidget.value()
        if not info == self.specifier.name:
            self.feature_system_changed = True
            alert = QMessageBox()
            alert.setWindowTitle('Warning!')
            alert.setText('Changing your feature system may cause changes to the way your Inventory chart is organized.')
            alert.setInformativeText('Do you want to continue?')
            alert.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            alert.setDefaultButton(QMessageBox.No)
            result = alert.exec_()
            if result == QMessageBox.No:
                self.resetFeatureWidget()
                return #Cancel changes
        else:
            self.feature_system_changed = False

        if self.specifier is not None:
            path = system_name_to_path(self.settings['storage'],self.specifier.name)
            save_binary(self.specifier, path)
        QDialog.accept(self)

    def help(self):
        url = get_url('transcriptions and feature systems', section='applying-editing-feature-systems')
        webbrowser.open(url)
        #self.helpDialog = HelpDialog(self,name = 'transcriptions and feature systems',
        #                            section = 'applying-editing-feature-systems')
        #self.helpDialog.exec_()


    def changeDisplay(self):
        if self.specifier is None:
            return
        mode = self.displayWidget.currentText()
        self.table.deleteLater()
        if mode == 'Tree':
            self.table = SubTreeView()
            self.table.setModel(FeatureSystemTreeModel(self.specifier))
            self.layout().insertWidget(0,self.table)
        elif mode == 'Matrix':
            self.table = TableWidget()
            self.table.setModel(FeatureSystemTableModel(self.specifier))
            self.table.resizeColumnsToContents()
            self.layout().insertWidget(0,self.table)

    def changeRestrictedFeatureSystem(self):
        if self.specifier is not None and self.changeWidget.systems.currentText() == self.specifier.name:
            return

        path = self.changeWidget.path()
        if self.specs_changed:
            alert = QMessageBox()
            alert.setWindowTitle('Feature system changed')
            alert.setText(('You have made some changes to the current feature system. If you swap systems now, '
            'you will lose those changes. What do you want to do?'))
            alert.addButton('Swap systems, lose changes', QMessageBox.YesRole)
            cancel = alert.addButton('Cancel, go back and save changes', QMessageBox.NoRole)
            alert.exec_()
            if alert.clickedButton() == cancel:
                self.resetRestrictedFeatureWidget()
                return

        if path is None:
            self.specifier = None
        else:
            self.specifier = load_binary(path)
            self.specifier = modernize.modernize_specifier(self.specifier)
        self.specs_changed = False
        self.changeDisplay()

    def changeFeatureSystem(self):

        path = self.changeWidget.path()

        if path is None:
            self.specifier = None
            return

        #Special case for when user has loaded corpus without a feature file
        if self.specifier is None:
            if os.path.exists(path):
                new_specifier = load_binary(path)
                self.specifier = new_specifier
                self.specifier = modernize.modernize_specifier(self.specifier)
                self.changeDisplay()
                return
            else:
                QMessageBox.critical(self, 'File not found', 'PCT could not find a feature file with the '
                'transcription and feature systems that you selected. Please select a different combination.\n\n'
                'You might be able to download the file you want by going to File > Manage feature systems...')
                self.resetFeatureWidget()
                return

        unmatched = list()
        if os.path.exists(path):
            new_specifier = load_binary(path)
            if new_specifier.name == self.specifier.name:
                return
            # even if a file exists, it is still possible that some of the segments in the current corpus have feature
            # specifications that do not match anything in the new feature system, so we have to check on that
            # for instance, if you're trying to take something with implosives in ipa2spe and turn it into arpbabet
            # which has no way of representing implosives
            unmatched = self.mapExistingSystems(new_specifier)
            if not unmatched:
                self.specifier = new_specifier
                self.specifier = modernize.modernize_specifier(self.specifier)
                self.changeDisplay()


        if not os.path.exists(path) or unmatched:
            #there is no existing feature file with the transcription/features combination that the user requested
            #so we will offer the choice of creating that new system now
            #or else the previous step of looking up a transcription failed for some segments
            filename = os.path.split(path)[-1]
            trans_name, feature_name = filename.split('2')
            feature_name = feature_name.split('.')[0]
            change = self.createNewSystem(trans_name, feature_name, filename)  # self.specifier is set somewhere in here
            if change:
                self.changeDisplay()
            else:
                self.resetFeatureWidget()

        return

    def resetFeatureWidget(self):
        pos = self.changeWidget.transSystem.findText(self.specifier.trans_name)
        self.changeWidget.transSystem.setCurrentIndex(pos)
        pos = self.changeWidget.featureSystem.findText(self.specifier.feature_name)
        self.changeWidget.featureSystem.setCurrentIndex(pos)

    def resetRestrictedFeatureWidget(self):
        pos = self.changeWidget.systems.findText(self.specifier.name)
        self.changeWidget.systems.setCurrentIndex(pos)

    def mapExistingSystems(self, new_specifier):
        unmatched = list()

        #IF THE TRANSCRIPTIONS MATCH, THEN MAP BASED ON SYMBOLS
        if new_specifier.trans_name == self.specifier.trans_name:
            unmatched = [seg for seg in self.specifier.matrix.keys() if not seg in new_specifier.matrix.keys()]

        #IF THE FEATURES MATCH, THEN MAP BASED ON FEATURES
        elif new_specifier.feature_name == self.specifier.feature_name:
            for seg,features in self.specifier.matrix.items():
                for seg2,features2 in new_specifier.matrix.items():
                    if features == features2:
                        self.segmap[seg] = seg2
                        break
                else:
                    unmatched.append(seg)

        unmatched = [seg for seg in unmatched if seg in self.corpus.inventory]

        return unmatched


    def createNewSystem(self, trans_name, feature_name, file_not_found_name):
        #this is called if the user has selected a transcription and feature system for which there is no built-in
        #feature file. it will create a new one called trans_name2feature_name.feature, based on the function arguments

        alert = QMessageBox()
        alert.setWindowTitle('Transcription/Feature mismatch')
        alert.setText(('PCT doesn\'t know how to match up the transcription symbols of your current corpus with '
                       'with appropriate symbols or features in {}.\n\n'
                       'It may be possible to download the feature file you need. Go to File > Manage feature '
                       'systems... and click on "Download". You can also import your own feature files from that menu screen. '
                       '\n\nAlternatively, you can tell PCT which symbols in the current {} system match the new {} '
                       'system, and a new feature file will be generated right now.'
                       ''.format(trans_name, self.specifier.name.split('2')[0], trans_name)))
        reject_button = alert.addButton('Go back to the previous window', QMessageBox.RejectRole)
        alert.addButton('Match transcription symbols now', QMessageBox.AcceptRole)
        alert.exec_()
        if alert.clickedButton() == reject_button:
            return False

        #User wants to map to new symbols
        systems = get_systems_list(self.settings['storage'])
        for system in systems:
            if trans_name in system.split('2')[0]:
                trans_system = load_binary(system_name_to_path(self.settings['storage'], system))
                new_symbols = list(trans_system.matrix.keys())
                new_symbols.sort()
                break

        dialog = RetranscribeWidget(self.corpus.inventory.segs, new_symbols,
                                    self.specifier.name.split('2')[0], trans_name)
        results = dialog.exec_()
        if results:
            self.segmap = dialog.segmap
            self.defaultFeatureFill(trans_name, feature_name, new_symbols)
        else:
            self.segmap = dict()

        return True

    def defaultFeatureFill(self, trans_name, feature_name, new_symbols):

        default = 'n'
        featureline = self.specifier.features
        for name in ['symbol', 'segment']:
            try:
                featureline.remove(name)
            except ValueError:
                pass
        defaultline = '\t'.join([default for feature in featureline])
        featureline = '\t'.join(featureline)
        new_system_name = '{}2{}'.format(trans_name, feature_name)
        new_path = os.path.join(self.settings['storage'], 'FEATURE', new_system_name + '.txt')
        inverse_segmap = {v: k for k, v in self.segmap.items()}

        with open(new_path, encoding='utf-8-sig', mode='w') as f:
            print('symbol\t{}'.format(featureline), file=f)
            for seg in new_symbols:
                if seg in inverse_segmap:
                    line = '\t'.join([seg] + self.specifier.seg_to_feat_line(inverse_segmap[seg])[1:])
                    print(line, file=f)
                else:
                    print('{}\t{}'.format(seg, defaultline), file=f)
        matrix = load_feature_matrix_csv(new_system_name, new_path, '\t')
        self.specifier = matrix

    def addSegment(self):
        if self.specifier is None:
            return
        dialog = EditSegmentDialog(self,self.table.model().specifier)
        if dialog.exec_():
            self.table.model().addSegment(dialog.seg,dialog.featspec)
            self.specs_changed = True

    def editSegment(self):
        if self.specifier is None:
            return
        if self.displayWidget.currentText() == 'Tree':
            index = self.table.selectionModel().currentIndex()
            seg = self.table.model().data(index,Qt.DisplayRole)
            if seg is None:
                return
            if seg not in self.specifier:
                return
        else:
            selected = self.table.selectionModel().selectedRows()
            if not selected:
                return
            selected = selected[0]
            seg = self.table.model().data(self.table.model().createIndex(selected.row(),0),Qt.DisplayRole)

        dialog = EditSegmentDialog(self,self.table.model().specifier,seg)
        if dialog.exec_():
            self.table.model().addSegment(dialog.seg,dialog.featspec)
            self.specs_changed = True

    def addFeature(self):
        if self.specifier is None:
            return
        dialog = AddFeatureDialog(self,self.table.model().specifier)
        if dialog.exec_():
            self.table.model().addFeature(dialog.featureName, dialog.defaultValue)
            self.specs_changed = True

    def hide(self):
        if self.specifier is None:
            return
        self.table.model().filter(self.corpus.inventory)

    def showAll(self):
        if self.specifier is None:
            return
        self.table.model().showAll()

    def checkCoverage(self):
        if self.specifier is None:
            return
        corpus_inventory = self.corpus.inventory
        try:
            feature_inventory = self.specifier.segments
        except AttributeError:
            reply = QMessageBox.warning(self,
                    "Missing feature system", "No feature system has been specified.")
        missing = []
        neutralized = []
        for seg in corpus_inventory:
            if seg.symbol == '#':
                continue
            if seg not in feature_inventory:
                for symbol,name in punctuation_names.items():
                    if str(seg) == symbol:
                        missing.append('{} ({})'.format(symbol, name))
                else:
                    missing.append(str(seg))
            elif all([f=='n' for f in self.specifier[seg.symbol].values()]):
                for symbol,name in punctuation_names.items():
                    if str(seg) == symbol:
                        neutralized.append('{} ({})'.format(symbol, name))
                else:
                    neutralized.append(str(seg))

        message = ['Some segments in your corpus are not fully specified.']
        if missing:
            message.append('\nThe following segments have not been specified for at least one feature:')
            message.append(','.join(missing))
        if neutralized:
            message.append('\nThe following segments have a value of "n" for all features:')
            message.append(','.join(neutralized))

        if missing or neutralized:
            reply = QMessageBox()
            reply.setWindowTitle('Missing segment information')
            reply.setText('\n'.join(message))
        else:
            reply = QMessageBox.information(self,
                    "Complete", 'All segments are specified for all features!')
        try:
            reply.exec_()
        except AttributeError:
            pass
            #An exception is raised when the user hits cancel (sometimes?). It's this one:
            #AttributeError: 'StandardButton' objects has no attribute 'exec_'


class CategoryWidget(QWidget):
    def __init__(self, category, features, specifier, parent = None):
        QWidget.__init__(self, parent)

        self.specifier = specifier
        self.category = category
        layout = QHBoxLayout()

        self.searchWidget = FeatureEdit(self.specifier, clearOnEnter = False)
        self.completer = FeatureCompleter(self.specifier)
        self.searchWidget.setCompleter(self.completer)
        if isinstance(features, dict):
            self.searchWidget.setText(', '.join(v+k for k,v in features.items()))
        elif isinstance(features, list):
            self.searchWidget.setText(', '.join(features))
        elif isinstance(features, str):
            self.searchWidget.setText(features)

        layout.addWidget(self.searchWidget)

        self.previewWidget = QLabel('Mouseover for included segments')
        self.previewWidget.setFrameShape(QFrame.Box)

        self.updateSegments()
        self.searchWidget.featureEntered.connect(self.updateSegments)

        layout.addWidget(self.previewWidget)
        self.setLayout(layout)

    def updateSegments(self, features = None):
        if features is None:
            features = self.searchWidget.features()
        if len(features) == 0:
            self.previewWidget.setToolTip('No included segments')
        else:
            segments = self.specifier.features_to_segments(features)
            self.previewWidget.setToolTip(', '.join(segments))

    def features(self):
        return self.searchWidget.features()

    def value(self):
        return self.category, self.searchWidget.features()

class EditCategoriesDialog(QDialog):
    def __init__(self, parent, specifier):
        QDialog.__init__(self, parent)
        self.specifier = specifier

        layout = QVBoxLayout()
        self.tabWidget = QTabWidget()

        midlayout = QHBoxLayout()

        catlayout = QFormLayout()

        self.vowelWidget = CategoryWidget('Vowel', self.specifier.vowel_feature, specifier)
        catlayout.addRow('Feature specifying vowels',self.vowelWidget)

        self.voiceWidget = CategoryWidget('Voiced', self.specifier.voice_feature, specifier)
        catlayout.addRow('Feature specifying voiced obstruents',self.voiceWidget)

        self.diphWidget = CategoryWidget('Diphthong', self.specifier.diph_feature, specifier)
        catlayout.addRow('Feature specifying diphthongs',self.diphWidget)

        self.roundedWidget = CategoryWidget('Rounded', self.specifier.rounded_feature, specifier)
        catlayout.addRow('Feature specifying rounded vowels',self.roundedWidget)

        catFrame = QWidget()
        catFrame.setLayout(catlayout)
        self.tabWidget.addTab(catFrame,'Major distinctions')


        placesFrame = QWidget()
        placeslayout = QFormLayout()

        self.places = []
        self.manners = []
        self.height = []
        self.backness = []

        for k,v in self.specifier.places.items():
            w = CategoryWidget(k, v, specifier)
            placeslayout.addRow(k, w)
            self.places.append(w)

        placesFrame.setLayout(placeslayout)
        self.tabWidget.addTab(placesFrame,'Places of articulation')

        mannersFrame = QWidget()
        mannerslayout = QFormLayout()
        for k,v in self.specifier.manners.items():
            w = CategoryWidget(k, v, specifier)
            mannerslayout.addRow(k, w)
            self.manners.append(w)

        mannersFrame.setLayout(mannerslayout)
        self.tabWidget.addTab(mannersFrame,'Manners of articulation')

        heightFrame = QWidget()
        heightlayout = QFormLayout()
        for k,v in self.specifier.height.items():
            w = CategoryWidget(k, v, specifier)
            heightlayout.addRow(k, w)
            self.height.append(w)

        heightFrame.setLayout(heightlayout)
        self.tabWidget.addTab(heightFrame,'Vowel height')

        backnessFrame = QWidget()
        backnesslayout = QFormLayout()
        for k,v in self.specifier.backness.items():
            w = CategoryWidget(k, v, specifier)
            backnesslayout.addRow(k, w)
            self.backness.append(w)

        backnessFrame.setLayout(backnesslayout)
        self.tabWidget.addTab(backnessFrame,'Vowel backness')

        midlayout.addWidget(self.tabWidget)

        layout.addLayout(midlayout)

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
        self.setWindowTitle('Edit categories')
        self.setLayout(layout)

    def vowel(self):
        return self.vowelWidget.features()

    def voiced(self):
        return self.voiceWidget.features()

    def rounded(self):
        return self.roundedWidget.features()

    def diphthong(self):
        return self.diphWidget.features()

    def value(self):
        p = {w.category: w.features() for w in self.places}
        m = {w.category: w.features() for w in self.manners}
        h = {w.category: w.features() for w in self.height}
        b = {w.category: w.features() for w in self.backness}
        return p, m, h, b


class EditSegmentDialog(QDialog):
    def __init__(self, parent, specifier, segment = None):
        QDialog.__init__(self, parent)

        self.specifier = specifier
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        featLayout = QGridLayout()
        self.symbolEdit = QLineEdit()
        self.add = True
        if segment is not None:
            self.add = False
            self.symbolEdit.setText(segment)
        box = QFrame()
        lay = QFormLayout()
        lay.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        lay.addRow('Symbol',self.symbolEdit)
        self.setAllSelect = QComboBox()
        self.setAllSelect.addItem(specifier.default_value)
        for i,v in enumerate(specifier.possible_values):
            if v == specifier.default_value:
                continue
            self.setAllSelect.addItem(v)
        self.setAllSelect.currentIndexChanged.connect(self.setAll)
        lay.addRow('Set all feature values to:',self.setAllSelect)
        box.setLayout(lay)
        layout.addWidget(box, alignment = Qt.AlignLeft)
        row = 0
        col = 0
        self.featureSelects = dict()
        for f in specifier.features:
            box = QGroupBox(f)
            box.setFlat(True)
            lay = QVBoxLayout()

            featSel = QComboBox()

            featSel.addItem(specifier.default_value)
            for i,v in enumerate(specifier.possible_values):
                if v == specifier.default_value:
                    continue
                featSel.addItem(v)
            for i in range(featSel.count()):
                if segment is not None and featSel.itemText(i) == specifier[segment][f]:
                    featSel.setCurrentIndex(i)
            lay.addWidget(featSel)
            box.setLayout(lay)
            self.featureSelects[f] = featSel
            featLayout.addWidget(box,row,col)

            col += 1
            if col > 6:
                col = 0
                row += 1

        featBox = QFrame()
        featBox.setLayout(featLayout)
        layout.addWidget(featBox)

        self.acceptButton = QPushButton('Ok')
        self.acceptButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton, alignment = Qt.AlignCenter)
        acLayout.addWidget(self.cancelButton, alignment = Qt.AlignCenter)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame, alignment = Qt.AlignCenter)

        self.setLayout(layout)
        if segment is not None:
            self.setWindowTitle('Edit segment')
        else:
            self.setWindowTitle('Add segment')

    def setAll(self):
        all_val = self.setAllSelect.currentIndex()
        for v in self.featureSelects.values():
            v.setCurrentIndex(all_val)

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
    def __init__(self, parent, settings, current_system):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout()
        self.settings = settings
        self.current_system = current_system
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
        self.downloadButton.setAutoDefault(False)
        self.loadFromCsvButton = QPushButton('Create feature system from text file')
        self.loadFromCsvButton.setAutoDefault(False)
        self.removeButton = QPushButton('Remove selected feature system')
        self.removeButton.setAutoDefault(False)
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
        self.helpButton = QPushButton('Help')
        self.acceptButton.setDefault(True)
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.helpButton)
        self.acceptButton.clicked.connect(self.accept)
        self.helpButton.clicked.connect(self.help)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        note = QLabel('This window is only for adding and removing transcription/features systems.\n'
                      'When loading a corpus, you will be asked which one of these systems you want to use with your '
                      'corpus. If you have an existing corpus and you want to change systems, go to '
                      'the Features menu and select View/change feature system...')
        note.setWordWrap(True)
        layout.addWidget(note)

        self.setLayout(layout)

        self.setWindowTitle('Manage feature systems')

    def help(self):
        url = get_url('transcriptions and feature systems')
        webbrowser.open(url)
        #self.helpDialog = HelpDialog(self, name = 'transcriptions and feature systems')
        #self.helpDialog.exec_()

    def openCsvWindow(self):
        dialog = SystemFromCsvDialog(self,self.settings)
        result = dialog.exec_()
        if result:
            self.getAvailableSystems()

    def openDownloadWindow(self):
        dialog = DownloadFeatureMatrixDialog(self,self.settings)
        result = dialog.exec_()
        if result:
            self.getAvailableSystems()

    def removeSystem(self):
        featureSystem = self.systemsList.currentItem()
        if featureSystem is None:
            return
        else:
            featureSystem = featureSystem.text()
        if self.current_system == featureSystem:
            alert = QMessageBox(QMessageBox.Warning, 'Remove system', 'This feature system is being used by your open '
            'corpus, and you cannot remove it. Please close your corpus first.')
            alert.addButton('OK', QMessageBox.AcceptRole)
            alert.exec_()
            return
        msgBox = QMessageBox(QMessageBox.Warning, "Delete feature file",
                "This will permanently remove '{}'.\n\n"
                "Unfortunately, PCT cannot automatically verify if you have any corpora "
                "that depend on these features, so you should only delete this if you are "
                "absolutely certain.".format(featureSystem),
                             QMessageBox.NoButton, self)
        msgBox.addButton("Delete this file", QMessageBox.AcceptRole)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        if msgBox.exec_() != QMessageBox.AcceptRole:
            return
        os.remove(system_name_to_path(self.settings['storage'],featureSystem))
        self.getAvailableSystems()


    def getAvailableSystems(self):
        self.systemsList.clear()
        systems = get_systems_list(self.settings['storage'])
        for s in systems:
            self.systemsList.addItem(s)

class SystemFromCsvDialog(PCTDialog):
    def __init__(self, parent, settings):
        PCTDialog.__init__(self, parent)

        self.settings = settings
        layout = QVBoxLayout()

        formLayout = QFormLayout()


        self.pathWidget = FileWidget('Open feature system csv','Text files (*.txt *.csv)')

        formLayout.addRow(QLabel('Path to feature system'),self.pathWidget)

        self.featureSystemSelect = FeatureSystemSelect(self.settings, add=True)

        formLayout.addRow(self.featureSystemSelect)

        self.columnDelimiterEdit = QLineEdit()
        self.columnDelimiterEdit.setText('\\t')
        formLayout.addRow(QLabel('Column delimiter (enter \'\\t\' for tab)'),self.columnDelimiterEdit)

        formFrame = QFrame()
        formFrame.setLayout(formLayout)
        layout.addWidget(formFrame)

        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        self.helpButton = QPushButton('Help')
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.acceptButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.helpButton)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)

        self.setLayout(layout)

        self.setWindowTitle('Create feature system from csv')

        self.thread = LoadFeatureSystemWorker()
        self.thread.errorEncountered.connect(self.handleError)

        self.progressDialog.setWindowTitle('Importing corpus...')
        self.progressDialog.beginCancel.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.progressDialog.updateProgress)
        self.thread.updateProgressText.connect(self.progressDialog.updateText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)
        self.thread.finishedCancelling.connect(self.progressDialog.reject)

    def help(self):
        url = get_url('transcriptions and feature systems',
                      section='using-a-custom-feature-system')
        webbrowser.open(url)
        # self.helpDialog = HelpDialog(self,name = 'transcriptions and feature systems',
        #                             section = 'loading-a-custom-feature-system')
        # self.helpDialog.exec_()

    def generateKwargs(self):
        kwargs = {}
        path = self.pathWidget.value()
        if path == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a path to the csv file.")
            return
        if not os.path.exists(path):
            reply = QMessageBox.critical(self,
                    "Invalid information", "Feature matrix file could not be located. Please verify the path and file name.")
            return
        kwargs['path'] = path
        name = self.featureSystemSelect.value()
        if name == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify the transcription and feature system.")
            return

        if name in get_systems_list(self.settings['storage']):
            msgBox = QMessageBox(QMessageBox.Warning, "Duplicate name",
                    "A feature system named '{}' already exists.  Overwrite?".format(name), QMessageBox.NoButton, self)
            msgBox.addButton("Overwrite", QMessageBox.AcceptRole)
            msgBox.addButton("Abort", QMessageBox.RejectRole)
            if msgBox.exec_() != QMessageBox.AcceptRole:
                return None
        if not name:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a name for the transcription and feature systems.")
            return
        kwargs['name'] = name
        colDelim = codecs.getdecoder("unicode_escape")(self.columnDelimiterEdit.text())[0]
        if not colDelim:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a column delimiter.")
            return
        kwargs['delimiter'] = colDelim
        return kwargs

    def setResults(self, results):
        self.specifier = results

    def accept(self):
        kwargs = self.generateKwargs()
        if kwargs is None:
            return
        self.thread.setParams(kwargs)

        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            if self.specifier is not None:
                save_binary(self.specifier,
                    system_name_to_path(self.settings['storage'],self.specifier.name))
            QDialog.accept(self)


