
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QPushButton,QWidget
from PyQt5.QtCore import QSettings,QSize,QPoint

from corpustools.config import CONFIG_PATH


class Settings(object):

    key_to_ini = {'storage': ('storage/directory',''),
                    'size':('display/size', QSize(270, 225)),
                    'pos': ('display/pos', QPoint(50, 50)),
                    'warnings': ('display/warnings',1),
                    'tooltips': ('display/tooltips',1)}

    def __init__(self):
        self.qs = QSettings(CONFIG_PATH,QSettings.IniFormat)
        self.qs.setFallbacksEnabled(False)

    def __getitem__(self, key):

        mapped_key = self.key_to_ini[key]
        if isinstance(mapped_key, list):
            return tuple(type(d)(self.qs.value(k,d)) for k, d in mapped_key)
        else:
            inikey, default = mapped_key
            return type(default)(self.qs.value(inikey,default))

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

class PreferencesDialog(QDialog):

    def __init__(self, parent, settings):
        QDialog.__init__( self, parent )

        self.settings = settings

        layout = QVBoxLayout()

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

    def accept(self):

        QDialog.accept(self)
