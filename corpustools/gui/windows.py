import sys
import subprocess
import time
import datetime

from .imports import *

from .helpgui import HelpDialog

from corpustools.corpus.io import download_binary

from corpustools.exceptions import PCTError, PCTPythonError

class ProgressDialog(QProgressDialog):
    beginCancel = Signal()
    def __init__(self, parent):
        QProgressDialog.__init__(self, parent)
        self.cancelButton = QPushButton('Cancel')
        self.setAutoClose(False)
        self.setAutoReset(False)
        self.setCancelButton(self.cancelButton)

        self.information = ''
        self.startTime = None

        self.rates = list()
        self.eta = None

        self.beginCancel.connect(self.updateForCancel)
        b = self.findChildren(QPushButton)[0]
        b.clicked.disconnect()
        b.clicked.connect(self.cancel)

    def cancel(self):
        self.beginCancel.emit()

    def updateForCancel(self):
        self.show()
        self.setMaximum(0)
        self.cancelButton.setEnabled(False)
        self.cancelButton.setText('Canceling...')
        self.setLabelText('Canceling...')

    def reject(self):
        QProgressDialog.cancel(self)

    def updateText(self,text):
        if self.wasCanceled():
            return
        self.information = text
        eta = 'Unknown'

        self.setLabelText('{}\nTime left: {}'.format(self.information,eta))

    def updateProgress(self, progress):
        if self.wasCanceled():
            return
        if progress == 0:
            self.setMaximum(100)
            self.cancelButton.setText('Cancel')
            self.cancelButton.setEnabled(True)
            self.startTime = time.time()

            self.eta = None
        else:
            elapsed = time.time() - self.startTime
            self.rates.append(elapsed / progress)
            self.rates = self.rates[-20:]
            if len(self.rates) > 18:

                rate = sum(self.rates)/len(self.rates)
                eta = int((1 - progress) * rate)
                if self.eta is None:
                    self.eta = eta
                if eta < self.eta or eta > self.eta + 10:
                    self.eta = eta
        self.setValue(progress*100)
        if self.eta is None:
            eta = 'Unknown'

        else:
            if self.eta < 0:
                self.eta = 0
            eta = str(datetime.timedelta(seconds = self.eta))
        self.setLabelText('{}\nEstimated time left: {}'.format(self.information,eta))

class FunctionWorker(QThread):
    updateProgress = Signal(object)
    updateProgressText = Signal(str)
    errorEncountered = Signal(object)
    finishedCancelling = Signal()

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
        elif isinstance(args[0],dict):
            self.updateProgressText.emit(args[0]['status'])
            return
        else:
            progress = args[0]
            if len(args) > 1:
                self.total = args[1]
        if self.total:
            self.updateProgress.emit((progress/self.total))

class PCTDialog(QDialog):

    def __init__(self, parent = None):
        QDialog.__init__(self, parent)

        self.progressDialog = ProgressDialog(self)


    def handleError(self,error):
        if isinstance(error, PCTError):
            if hasattr(error, 'main'):
                reply = QMessageBox()
                reply.setWindowTitle('Error encountered')
                reply.setIcon(QMessageBox.Critical)
                reply.setText(error.main)
                reply.setInformativeText(error.information)
                reply.setDetailedText(error.details)

                if hasattr(error,'print_to_file'):
                    error.print_to_file(self.parent().settings.error_directory())
                    reply.addButton('Open errors directory',QMessageBox.AcceptRole)
                reply.setStandardButtons(QMessageBox.Close)
                ret = reply.exec_()
                if ret == QMessageBox.AcceptRole:
                    error_dir = self.parent().settings.error_directory()
                    if sys.platform == 'win32':
                        args = ['{}'.format(error_dir)]
                        program = 'explorer'
                        #subprocess.call('explorer "{0}"'.format(self.parent().settings.error_directory()),shell=True)
                    elif sys.platform == 'darwin':
                        program = 'open'
                        args = ['{}'.format(error_dir)]
                    else:
                        program = 'xdg-open'
                        args = ['{}'.format(error_dir)]
                    #subprocess.call([program]+args,shell=True)
                    proc = QProcess(self.parent())
                    t = proc.startDetached(program,args)
            else:
                reply = QMessageBox.critical(self,
                        "Error encountered", str(error))
        else:
            reply = QMessageBox.critical(self,
                    "Error encountered", str(error))
        self.progressDialog.reject()
        return None

class FunctionDialog(PCTDialog):
    header = None
    _about = None
    name = ''
    def __init__(self,parent, settings, worker):
        PCTDialog.__init__(self, parent)
        self.settings = settings
        layout = QVBoxLayout()

        self.newTableButton = QPushButton('Calculate {}\n(start new results table)'.format(self.name))
        self.newTableButton.setDefault(True)
        self.oldTableButton = QPushButton('Calculate {}\n(add to current results table)'.format(self.name))
        self.cancelButton = QPushButton('Cancel')
        self.aboutButton = QPushButton('About {}...'.format(self.name))
        acLayout = QHBoxLayout()
        acLayout.addWidget(self.newTableButton)
        acLayout.addWidget(self.oldTableButton)
        acLayout.addWidget(self.cancelButton)
        acLayout.addWidget(self.aboutButton)
        self.newTableButton.clicked.connect(self.newTable)
        self.oldTableButton.clicked.connect(self.oldTable)
        self.aboutButton.clicked.connect(self.about)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(acLayout)

        layout.addWidget(acFrame)
        self.setLayout(layout)

        self.setWindowTitle(self.name.title())

        self.thread = worker
        self.thread.errorEncountered.connect(self.handleError)

        self.progressDialog.setWindowTitle('Calculating {}'.format(self.name))
        self.progressDialog.beginCancel.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.progressDialog.updateProgress)
        self.thread.updateProgressText.connect(self.progressDialog.updateText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)
        self.thread.finishedCancelling.connect(self.progressDialog.reject)

    def setResults(self, results):
        self.results = results

    def calc(self):
        raise(NotImplementedError)

    def newTable(self):
        self.update = False
        self.calc()

    def oldTable(self):
        self.update = True
        self.calc()

    def about(self):

        self.aboutWindow = HelpDialog(self, self.name)
        self.aboutWindow.exec_()
        #self.aboutWindow.raise_()
        #self.aboutWindow.activateWindow()
        #reply = QMessageBox.information(self,
        #        "About {}".format(self.name), '\n'.join(self._about))

class DownloadWorker(FunctionWorker):
    def run(self):
        if self.stopCheck():
            return
        self.results = download_binary(self.kwargs['name'],self.kwargs['path'], call_back = self.kwargs['call_back'])
        if self.stopCheck():
            return
        self.dataReady.emit(self.results)

class SelfUpdateWorker(FunctionWorker):
    def run(self):
        if self.stopCheck():
            return
        app = self.kwargs['app']
        app.auto_update(callback = self.kwargs['call_back'])
        if self.stopCheck():
            return
        self.dataReady.emit('')
