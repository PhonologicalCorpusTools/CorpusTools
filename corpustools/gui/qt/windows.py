
from PyQt5.QtCore import pyqtSignal as Signal,QThread
from PyQt5.QtWidgets import (QDialog, QListWidget, QGroupBox, QHBoxLayout,
                            QVBoxLayout, QPushButton, QFrame, QGridLayout,
                            QRadioButton, QLabel, QFormLayout, QLineEdit,
                            QFileDialog, QComboBox,QProgressDialog, QCheckBox,
                            QMessageBox)

class FunctionWorker(QThread):
    updateProgress = Signal(int)
    updateProgressText = Signal(str)

    dataReady = Signal(object)

    def __init__(self):
        QThread.__init__(self)
        self.stopped = False

    def setParams(self, kwargs):
        self.kwargs = kwargs
        self.kwargs['call_back'] = self.emitProgress
        self.kwargs['stop_check'] = self.stopCheck
        self.stopped = False
        self.total = None

    def stop(self):
        self.stopped = True

    def stopCheck(self):
        return self.stopped

    def emitProgress(self,*args):
        if isinstance(args[0],str):
            self.updateProgressText.emit(args[0])
            return
        else:
            progress = args[0]
            if len(args) > 1:
                self.total = args[1]
        if self.total:
            self.updateProgress.emit(int((progress/self.total)*100))

class FunctionDialog(QDialog):
    header = None
    ABOUT = None
    def __init__(self,functionName,parent):
        pass

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def calc(self):
        raise(NotImplementedError)

    def newTable(self):
        self.update = False
        self.calc()

    def oldTable(self):
        self.update = True
        self.calc()
