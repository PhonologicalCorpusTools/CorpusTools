import os
import collections
import shutil

from .imports import *
#from .widgets import DirectoryWidget
import corpustools.gui.widgets as PCTWidgets

class BasePane(QWidget):
    """Abstract, don't use"""

    prev_state = {}

    def get_current_state(self):
        return None

    def is_changed(self):
        return self.get_current_state() != self.prev_state

    def validate(self):
        pass


class StoragePane(BasePane):
    def __init__(self, setting_dict):
        BasePane.__init__( self )

        layout = QFormLayout()

        self.storageDirectoryWidget = PCTWidgets.DirectoryWidget()

        layout.addRow(QLabel('Storage directory:'),self.storageDirectoryWidget)

        self.setLayout(layout)

        #set up defaults

        storageDirectory = setting_dict['storage']

        self.storageDirectoryWidget.setPath(storageDirectory)

        self.prev_state = setting_dict

    def validate(self):
        root = os.path.dirname(self.storageDirectoryWidget.value())
        if not os.path.exists(root):
            raise(Exception('The specified directory\'s parent directory ({}) does not exist.'.format(root)))

    def get_current_state(self):
        setting_dict = {}

        setting_dict['storage'] = self.storageDirectoryWidget.value()

        return setting_dict

class ReminderPane(BasePane):

    def __init__(self, setting_dict):
        BasePane.__init__(self)

        layout = QFormLayout()

        self.remindFeatureFile = QCheckBox()
        self.remindCorpusFile = QCheckBox()

        layout.addRow(QLabel('Always ask before overwriting a corpus'), self.remindCorpusFile)
        layout.addRow(QLabel('Always ask before overwriting a feature file'), self.remindFeatureFile)

        self.setLayout(layout)

        self.remindFeatureFile.setChecked(int(setting_dict['ask_overwrite_features']))
        self.remindFeatureFile.setChecked(int(setting_dict['ask_overwrite_features']))
        self.remindCorpusFile.setChecked(int(setting_dict['ask_overwrite_corpus']))

    def get_current_state(self):
        settings_dict = {}
        settings_dict['ask_overwrite_features'] = int(self.remindFeatureFile.isChecked())
        settings_dict['ask_overwrite_corpus'] = int(self.remindCorpusFile.isChecked())
        return settings_dict

class DisplayPane(BasePane):
    def __init__(self, setting_dict):
        BasePane.__init__( self )

        layout = QFormLayout()

        self.sigfigWidget = QLineEdit()
        self.sigfigWidget.setValidator(QDoubleValidator(float('inf'), 0, 0))
        self.displayAllWidget = QCheckBox()
        displayAllLabel = QLabel('Display entire inventory in results when "Match single wildcard" is selected')
        displayAllLabel.setWordWrap(True)

        layout.addRow(QLabel('Number of displayed decimal places:'),self.sigfigWidget)
        layout.addRow(displayAllLabel, self.displayAllWidget)

        self.setLayout(layout)

        #set up defaults

        sigfigs = setting_dict['sigfigs']
        self.sigfigWidget.setText(str(sigfigs))

        self.displayAllWidget.setChecked(bool(setting_dict['show_full_inventory']))

        self.prev_state = setting_dict

    def validate(self):
        try:
            t = int(self.sigfigWidget.text())
        except ValueError:
            raise(Exception('Number of significant figures requires an integer'))

    def get_current_state(self):
        setting_dict = {}
        setting_dict['sigfigs'] = int(self.sigfigWidget.text())
        setting_dict['show_full_inventory'] = int(self.displayAllWidget.isChecked())
        return setting_dict

class ProcessingPane(BasePane):
    def __init__(self, setting_dict):
        BasePane.__init__( self )

        layout = QFormLayout()

        self.usemultiCheck = QCheckBox()

        layout.addRow(QLabel('Use multiprocessing (where available)'),self.usemultiCheck)

        self.numcoresWidget = QLineEdit()
        self.numcoresWidget.setValidator(QDoubleValidator(float('inf'), 0, 0))

        layout.addRow(QLabel('Number of cores to use\n(Set to 0 to use 3/4 of the available cores):'),self.numcoresWidget)

        self.setLayout(layout)

        #set up defaults

        use_multi = setting_dict['use_multi']
        num_cores = setting_dict['num_cores']

        self.usemultiCheck.setChecked(int(use_multi))

        self.numcoresWidget.setText(str(num_cores))

        self.prev_state = setting_dict

    def get_current_state(self):
        setting_dict = {}
        setting_dict['use_multi'] = int(self.usemultiCheck.isChecked())
        setting_dict['num_cores'] = int(self.numcoresWidget.text())

        return setting_dict

class ResultsDisplayPane(BasePane):

    def __init__(self, setting_dict):
        BasePane.__init__(self)

        layout = QFormLayout()

        self.resultsDisplayUniqueFirst = QCheckBox()

        layout.addRow(QLabel('Always Display unique results first \n(unchecked will display results in a default order)'), self.resultsDisplayUniqueFirst)

        self.setLayout(layout)

        self.resultsDisplayUniqueFirst.setChecked(setting_dict['unique_first'])
        

    def get_current_state(self):
        settings_dict = {}
        settings_dict['unique_first'] = bool(self.resultsDisplayUniqueFirst.isChecked())
        return settings_dict


class PCTSettings(collections.defaultdict):
    shortcuts = {'storage': 'storage_folder/directory',
                  'praatpath': 'storage_folder/praat',
                  'searches': 'storage_folder/searches',
                  'size': 'display/size',
                  'pos': 'display/pos',
                  'sigfigs': 'display/sigfigs',
                  'warnings': 'reminders/warnings',
                  'tooltips': 'display/tooltips',
                  'show_full_inventory': 'display/searchResults',
                  'use_multi': 'multiprocessing/enabled',
                  'num_cores': 'multiprocessing/numcores',
                  'ask_overwrite_features': 'reminders/features',
                  'ask_overwrite_corpus': 'reminders/corpus',
                  'unique_first': 'resultsDisplay/unique_first'}

    storage_setting_keys = ['storage']

    display_setting_keys = ['sigfigs', 'tooltips', 'show_full_inventory']

    processing_setting_keys = ['use_multi', 'num_cores']

    reminder_setting_keys = ['ask_overwrite_features', 'ask_overwrite_corpus', 'warnings']

    results_display_setting_keys = ['unique_first']


    def __init__(self):
        super().__init__(dict)

    def __getitem__(self, key):
        if key in self.shortcuts:
            key1, key2 = self.shortcuts[key].split('/')
            #print(self)
            return self[key1][key2]
        else:
            return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key in self.shortcuts:
            key1, key2 = self.shortcuts[key].split('/')
            self[key1][key2] = value
        else:
            super().__setitem__(key, value)

    def update(self, other_dict):
        for key in other_dict:
            self[key] = other_dict[key]

    def error_directory(self):
        return os.path.join(self['storage_folder']['directory'],'ERRORS')

    def log_directory(self):
        return os.path.join(self['storage_folder']['directory'],'LOG')

    def feature_directory(self):
        return os.path.join(self['storage_folder']['directory'], 'FEATURE')

    def search_directory(self):
        return os.path.join(self['storage_folder']['directory'], 'SEARCH')

    def get_storage_settings(self):
        out = {x: self[x] for x in self.storage_setting_keys}
        return out

    def get_display_settings(self):
        out = {x: self[x] for x in self.display_setting_keys}
        return out

    def get_processing_settings(self):
        out = {x: self[x] for x in self.processing_setting_keys}
        return out

    def get_reminder_settings(self):
        out = {x: self[x] for x in self.reminder_setting_keys}
        return out

    def get_results_display_settings(self):
        out = {x: self[x] for x in self.results_display_setting_keys}
        return out

    def check_storage(self):
        if not os.path.exists(self['storage_folder']['directory']):
            os.makedirs(self['storage_folder']['directory'])
        LOG_DIR = self.log_directory()
        ERROR_DIR = self.error_directory()
        TMP_DIR = os.path.join(self['storage_folder']['directory'],'TMP')
        CORPUS_DIR = os.path.join(self['storage_folder']['directory'],'CORPUS')
        FEATURE_DIR = os.path.join(self['storage_folder']['directory'],'FEATURE')
        SEARCH_DIR = os.path.join(self['storage_folder']['directory'],'SEARCH')
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)
        if not os.path.exists(ERROR_DIR):
            os.mkdir(ERROR_DIR)
        if not os.path.exists(TMP_DIR):
            os.mkdir(TMP_DIR)
        if not os.path.exists(CORPUS_DIR):
            os.mkdir(CORPUS_DIR)
        if not os.path.exists(FEATURE_DIR):
            os.mkdir(FEATURE_DIR)
        if not os.path.exists(SEARCH_DIR):
            os.mkdir(SEARCH_DIR)

        if not os.listdir(CORPUS_DIR):      # If the CORPUS folder is empty
            self.init_datacopy(src="CORPUS", target=CORPUS_DIR)  # copy built-in corpora
        if not os.listdir(FEATURE_DIR):     # If the FEATURE folder is empty
            self.init_datacopy(src="FEATURE", target=FEATURE_DIR)  # copy built-in corpora

    def init_datacopy(self, src, target):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            example_dir = os.path.join(sys._MEIPASS, 'resources', src)
        else:
            example_dir = os.path.join('..', 'resources', src)
        example_list = [f for f in os.listdir(example_dir) if '.'+src.lower() in f]
        abs_target = os.path.abspath(target)
        for file in example_list:
            source = os.path.join(example_dir, file)
            source = os.path.abspath(source)  # turned rel path into absolute path
            shutil.copy(source, abs_target)

class PreferencesDialog(QDialog):

    def __init__(self, parent, settings):
        QDialog.__init__( self, parent )

        self.settings = settings

        tabWidget = QTabWidget()

        #Storage
        self.storeWidget = StoragePane(self.settings.get_storage_settings())

        tabWidget.addTab(self.storeWidget,'Storage')

        #Display
        self.displayWidget = DisplayPane(self.settings.get_display_settings())

        tabWidget.addTab(self.displayWidget,'Display')

        #Processing
        self.processingWidget = ProcessingPane(self.settings.get_processing_settings())

        tabWidget.addTab(self.processingWidget,'Processing')

        #Reminders
        self.reminderWidget = ReminderPane(self.settings)

        tabWidget.addTab(self.reminderWidget, 'Reminders')

        #Results Display
        self.resultsDisplayWidget = ResultsDisplayPane(self.settings.get_results_display_settings())

        tabWidget.addTab(self.resultsDisplayWidget, 'Results Display')



        layout = QVBoxLayout()
        layout.addWidget(tabWidget)
        #Accept cancel
        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')

        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        hbox = QHBoxLayout()
        hbox.addWidget(self.acceptButton)
        hbox.addWidget(self.cancelButton)
        ac = QWidget()
        ac.setLayout(hbox)
        layout.addWidget(ac)

        self.setLayout(layout)

        self.setWindowTitle('Edit preferences')

    def accept(self):
        try:
            self.storeWidget.validate()
            self.displayWidget.validate()
            self.processingWidget.validate()
        except Exception as e:
            reply = QMessageBox.critical(self,
                    "Invalid information", str(e))
            return

        QDialog.accept(self)
