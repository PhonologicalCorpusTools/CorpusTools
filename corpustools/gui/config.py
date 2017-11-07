import os

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

        self.remindFeatureFile.setChecked(setting_dict['ask_overwrite_features'])
        self.remindFeatureFile.setChecked(setting_dict['ask_overwrite_features'])
        self.remindCorpusFile.setChecked(setting_dict['ask_overwrite_corpus'])

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
        self.displayAllWidget = QCheckBox()
        displayAllLabel = QLabel('Display entire inventory in results when "Match any segment" is selected')
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

        layout.addRow(QLabel('Number of cores to use\n(Set to 0 to use 3/4 of the available cores):'),self.numcoresWidget)

        self.setLayout(layout)

        #set up defaults

        use_multi = setting_dict['use_multi']
        num_cores = setting_dict['num_cores']

        self.usemultiCheck.setChecked(use_multi)

        self.numcoresWidget.setText(str(num_cores))

        self.prev_state = setting_dict

    def get_current_state(self):
        setting_dict = {}

        setting_dict['use_multi'] = int(self.usemultiCheck.isChecked())
        setting_dict['num_cores'] = int(self.numcoresWidget.text())

        return setting_dict

class Settings(object):

    key_to_ini = {'storage': ('storage/directory',os.path.normpath(os.path.join(
                                            os.path.expanduser('~/Documents'),'PCT','CorpusTools'))),
                    'praatpath': ('storage/praat',''),
                    'size':('display/size', QSize(270, 225)),
                    'pos': ('display/pos', QPoint(50, 50)),
                    'sigfigs': ('display/sigfigs',3),
                    'warnings': ('reminders/warnings',1),
                    'tooltips': ('display/tooltips',1),
                    'show_full_inventory': ('display/searchResults', 0),
                    'use_multi': ('multiprocessing/enabled',0),
                    'num_cores': ('multiprocessing/numcores',1),
                    'ask_overwrite_features': ('reminders/features', 1),
                    'ask_overwrite_corpus': ('reminders/corpus', 1),
                    'saved_searches': ('searches/saved', None),
                    'recent_searches': ('searches/recent', None)}

    storage_setting_keys = ['storage']

    display_setting_keys = ['sigfigs', 'tooltips', 'show_full_inventory']

    processing_setting_keys = ['use_multi','num_cores']

    reminder_setting_keys = ['ask_overwrite_features', 'ask_overwrite_corpus', 'warnings']

    search_keys = ['saved_searches', 'recent_searches']

    def __init__(self):
        self.qs = QSettings("PCT","Phonological CorpusTools")
        self.check_storage()

    def error_directory(self):
        return os.path.join(self['storage'],'ERRORS')

    def log_directory(self):
        return os.path.join(self['storage'],'LOG')

    def feature_directory(self):
        return os.path.join(self['storage'], 'FEATURE')

    def check_storage(self):
        if not os.path.exists(self['storage']):
            os.makedirs(self['storage'])
        LOG_DIR = self.log_directory()
        ERROR_DIR = self.error_directory()
        TMP_DIR = os.path.join(self['storage'],'TMP')
        CORPUS_DIR = os.path.join(self['storage'],'CORPUS')
        FEATURE_DIR = os.path.join(self['storage'],'FEATURE')
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

    def __getitem__(self, key):

        mapped_key = self.key_to_ini[key]
        if isinstance(mapped_key, list):
            return tuple(type(d)(self.qs.value(k,d)) for k, d in mapped_key)
        else:
            inikey, default = mapped_key
            if key in self.search_keys:
                if default is None:
                    return list()
            elif key == 'num_cores':
                if self['use_multi']:
                    return type(default)(self.qs.value(inikey,default))
                else:
                    return -1
            else:
                return type(default)(self.qs.value(inikey, default))

    def __setitem__(self, key, value):
        mapped_key = self.key_to_ini[key]
        if isinstance(mapped_key, list):
            if not isinstance(value,list) and not isinstance(value,tuple):
                raise(KeyError)
            if len(mapped_key) != len(value):
                raise(KeyError)
            for i,(k, d) in enumerate(mapped_key):
                self.qs.setValue(k,value[i])
        else:
            inikey, default = mapped_key
            self.qs.setValue(inikey,value)

    def sync(self):
        self.qs.sync()

    def update(self,setting_dict):
        for k,v in setting_dict.items():
            self[k] = v

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
        out = {x: self[x] for x in self.processing_setting_keys}
        return out

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

        self.settings.update(self.storeWidget.get_current_state())
        self.settings.update(self.displayWidget.get_current_state())
        self.settings.update(self.processingWidget.get_current_state())
        self.settings.update(self.reminderWidget.get_current_state())
        self.settings.check_storage()
        QDialog.accept(self)
