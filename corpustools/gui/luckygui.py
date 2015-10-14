from .imports import *
from .windows import FunctionWorker

from corpustools.symbolsim.string_similarity import string_similarity
from corpustools.funcload.functional_load import minpair_fl
from corpustools.phonoprob.phonotactic_probability import phonotactic_probability_vitevitch
from corpustools.kl.kl import KullbackLeibler

class UnLuckyError(Exception):
    pass

class LuckyWorker(FunctionWorker):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        if self.name == 'functional_load':
            try:
                results = minpair_fl(self.kwargs['corpus'], self.kwargs['segment_pair'],
                                     stop_check = self.kwargs['stop_check'],
                                     call_back = self.kwargs['call_back'])
                self.dataReady.emit(results)
            except Exception as e:
                message = '{}:{}'.format(self.name,e)
                self.errorEncountered.emit(message)
                return

        elif self.name == 'string_similarity':
            try:
                results = string_similarity(self.kwargs['corpus'], self.kwargs['query'], self.kwargs['algorithm'],
                                                        stop_check = self.kwargs['stop_check'],
                                                            call_back = self.kwargs['call_back'])
                self.dataReady.emit(results)
            except Exception as e:
                message = '{}:{}'.format(self.name,e)
                self.errorEncountered.emit(message)
                return

        elif self.name == 'phonotactic_probability':
            try:
                results = phonotactic_probability_vitevitch(self.kwargs['corpus'],self.kwargs['query'],
                                                            self.kwargs['sequence_type'],
                                                            probability_type=self.kwargs['probability_type'],
                                                            stop_check = self.kwargs['stop_check'],
                                                            call_back = self.kwargs['call_back'])
                self.dataReady.emit(results)
            except Exception as e:
                message = '{}:{}'.format(self.name,e)
                self.errorEncountered.emit(message)
                return

        elif self.name == 'kullback_leibler':
            try:
                results = KullbackLeibler(self.kwargs['corpus'], self.kwargs['seg1'], self.kwargs['seg2'], self.kwargs['side'],
                                          stop_check = self.kwargs['stop_check'],
                                            call_back = self.kwargs['call_back'])
                self.dataReady.emit(results)
            except Exception as e:
                message = '{}:{}'.format(self.name,e)
                self.errorEncountered.emit(message)
                return

        else:
            raise UnLuckyException('No analysis function called {} could be found'.format(self.name))


class LuckyDialog(QDialog):

    def __init__(self, parent, func_name, kwargs):
        super().__init__()
        self.resultsList = list()
        self.func_name = func_name
        self.kwargs = kwargs
        self.thread = LuckyWorker(func_name)
        self.thread.errorEncountered.connect(self.handleError)
        self.setWindowTitle('Found something!')

        self.progressDialog = QProgressDialog('Looking for something interesting...',
                                                'Cancel',0,100, self)
        self.progressDialog.setWindowTitle('On a phonological treasure hunt')
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setAutoReset(False)
        self.progressDialog.canceled.connect(self.thread.stop)
        self.thread.updateProgress.connect(self.updateProgress)
        self.thread.updateProgressText.connect(self.updateProgressText)
        self.thread.dataReady.connect(self.setResults)
        self.thread.dataReady.connect(self.progressDialog.accept)

    def calc(self):
        self.thread.setParams(self.kwargs)
        self.thread.start()
        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            self.accept()
            getattr(self, self.func_name)()
            self.printResults()
        else:
            self.reject()
            print('Problem!')


    def setResults(self, results):
        self.results = results

    def updateProgressText(self, text):
        self.progressDialog.setLabelText(text)
        self.progressDialog.reset()

    def updateProgress(self,progress):
        self.progressDialog.setValue(progress)
        self.progressDialog.repaint()

    def handleError(self,error):

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
                    args = ['"{}"'.format(error_dir)]
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
        self.progressDialog.cancel()
        return None

    def functional_load(self):
        seg1,seg2 = self.kwargs['segment_pair']
        fl = self.results
        self.resultsList.append(QLabel('I noticed that your corpus has the sounds /{}/ and /{}/'.format(seg1,seg2)))
        self.resultsList.append(QLabel('So I decided to calculate their functional load'))
        self.resultsList.append(QLabel('The result is: {}'.format(fl)))
        if fl < 1:
            self.resultsList.append(QLabel('Doesn\'t look like there are too many minimal pairs between these sounds.'))
        else:
            self.resultsList.append(QLabel('Hey, there might be a few minimal pairs in there. Be a real shame if these sounds merged.'))
        self.resultsList.append(QLabel('Find out more about the functional load of sounds in your corpus by going to Analysis > Calculate functional load...'))

    def string_similarity(self):
        word = getattr(self.kwargs['query'], 'transcription')
        most = self.results[1]#results[0]==word, so not interesting
        least = self.results[-1]
        algorithm = 'Khorsi' if self.kwargs['algorithm'] == 'khorsi' else 'edit distance'

        self.resultsList.append(QLabel('I thought the word [{}] was interesting.'.format(word)))
        self.resultsList.append(QLabel('So I calculated its string similarity to other words in your corpus'))
        self.resultsList.append(QLabel('Using the {} algorithm, the word most related to it is [{}], scoring {}.'.format(algorithm,getattr(most[1],'transcription'),most[2])))
        self.resultsList.append(QLabel('And the word least related to it is [{}], scoring {}.'.format(getattr(least[1],'transcription'),least[2])))
        self.resultsList.append(QLabel('Find out the string similarity of other words by clicking on Analysis > Calculate string simliarity...'))

    def kullback_leibler(self):
        seg1 = self.kwargs['seg1']
        seg2 = self.kwargs['seg2']
        side = self.results[2]
        kl = self.results[5]
        is_spurious = self.results[7]

        if kl <= 0:
            kl_description = 'A value of 0 means the two sounds have identical distributions.'
        if kl <= 2.:
            kl_description = 'This is a low value, which means the sounds have very similiar distributions. They are probably phonemes.'
        else:
            if is_spurious == 'Yes':
                add = 'However, they are phonetically quite different, so they probably are not allophones'
            else:
                add = 'They are also phonetically similar, so they could be allophones'
            kl_description = 'These two sounds have very different distributions. {}'.format(add)


        self.resultsList.append(QLabel('Your corpus has the sounds [{}] and [{}]'.format(seg1,seg2)))
        self.resultsList.append(QLabel('I looked at how these sounds are distributed, using the Kullback-Leibler measure of dissimilarity of distributions'))
        self.resultsList.append(QLabel('The KL distance is {}'.format(kl)))
        self.resultsList.append(QLabel(kl_description))
        self.resultsList.append(QLabel('To see how other sounds are distributed, go to Analysis > Calculate Kullback-Leibler...'))

    def phonotactic_probability(self):
        word = self.kwargs['query']
        self.resultsList.append(QLabel('I decided to look at the phonotactics of the word [{}], using a {} model'.format(
                                                                           word, self.kwargs['probability_type'])))
        word = getattr(word, self.kwargs['sequence_type'])
        if self.kwargs['probability_type'] == 'unigram':
            self.resultsList.append(QLabel(('This means looking at how frequent [{}] is in 1st position in all the words in'
                                                'your corpus, then how frequent [{}] is in 2nd position, etc.'.format(word[0],word[1]))))
        else:
            self.resultsList.append(QLabel(('This means looking at the frequency of [{}] as the first pair of sounds in a word,'
                                            'the frequency of [{}] as the next pair of sounds, etc.'.format(word[0]+word[1], word[1]+word[2]))))

        self.resultsList.append(QLabel('In this case, the overall score is {}'.format(self.results)))

        # if self.results<.25:
        #     self.resultsList.append(QLabel('It turns out this is a rather unusual word. It matches less than 25% of your corpus'))
        # elif self.results <.75:
        #     self.resultsList.append(QLabel(('This looks like a pretty normal word. Sorry. I thought it might be more '
        #                                         'interesting. But don\'t give up hope. Close this window and try again')))
        # else:
        #     self.resultsList.append(QLabel('This word has phonotactic probabilities that are extremely common.'))

        self.resultsList.append(QLabel('Find out more about your corpus by going to Analysis > Calculate phonotactic probability...'))

    def printResults(self):
        layout = QVBoxLayout()
        for widget in self.resultsList:
            layout.addWidget(widget)
        self.setLayout(layout)

