
from .imports import *

from corpustools.corpus.io import download_binary

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
    _about = None
    name = ''
    def __init__(self,parent, worker):
        QDialog.__init__(self, parent)

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

        self.progressDialog = QProgressDialog('Calculating {}...'.format(self.name),'Cancel',0,100, self)
        self.progressDialog.setWindowTitle('Calculating {}'.format(self.name))
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def setResults(self, results):
        self.results = results

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

    def about(self):
        reply = QMessageBox.information(self,
                "About {}".format(self.name), '\n'.join(self._about))

class DownloadWorker(FunctionWorker):
    def run(self):
        if self.stopCheck():
            return
        self.results = download_binary(self.kwargs['name'],self.kwargs['path'], call_back = self.kwargs['call_back'])
        if self.stopCheck():
            return
        self.dataReady.emit(self.results)
