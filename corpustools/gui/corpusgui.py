
import os
import pickle
import collections

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE, Toplevel, Listbox, OptionMenu, IntVar, Checkbutton )
from tkinter.ttk import Progressbar
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

from urllib.request import urlretrieve
import queue
import string

from corpustools.corpus.classes import (CorpusFactory, Corpus, FeatureSpecifier,
                                    Word, Segment)
from corpustools.gui.basegui import (AboutWindow, FunctionWindow,
                    ResultsWindow, MultiListbox, ThreadedTask, config, ERROR_DIR)

def get_corpora_list():
    corpus_dir = os.path.join(config['storage']['directory'],'CORPUS')
    corpora = [x.split('.')[0] for x in os.listdir(corpus_dir)]
    return corpora

class DownloadWindow(Toplevel):
    def __init__(self,master=None, **options):
        super(DownloadWindow, self).__init__(master=master, **options)
        self.corpus_button_var = StringVar()
        self.corpusq = queue.Queue()
        self.title('Download corpora')
        corpus_frame = Frame(self)
        corpus_area = LabelFrame(corpus_frame, text='Select a corpus')
        corpus_area.grid(sticky=W, column=0, row=0)
        subtlex_button = Radiobutton(corpus_area, text='Example', variable=self.corpus_button_var, value='example')
        subtlex_button.grid(sticky=W,row=0)
        subtlex_button.invoke()#.select() doesn't work on ttk.Button
        iphod_button = Radiobutton(corpus_area, text='IPHOD', variable=self.corpus_button_var, value='iphod')
        iphod_button.grid(sticky=W,row=1)
        corpus_frame.grid()

        button_frame = Frame(self)
        ok_button = Button(button_frame,text='OK', command=self.confirm_download)
        ok_button.grid(row=3, column=0)#, sticky=W, padx=3)
        cancel_button = Button(button_frame,text='Cancel', command=self.destroy)
        cancel_button.grid(row = 3, column=1)#, sticky=W, padx=3)
        button_frame.grid()

        warning_label = Label(self, text='Please be patient. It can take up to 30 seconds to download a corpus.')
        warning_label.grid()
        self.focus()

    def confirm_download(self):
        corpus_name = self.corpus_button_var.get()
        path = os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus')
        if corpus_name in get_corpora_list():
            carry_on = MessageBox.askyesno(message=(
                'This corpus is already available locally.  Would you like to redownload it?'))
            if not carry_on:
                return
            os.remove(path)
        if corpus_name == 'example':
            download_link = 'https://www.dropbox.com/s/a0uar9h8wtem8cf/example.corpus?dl=1'
        elif corpus_name == 'iphod':
            download_link = 'https://www.dropbox.com/s/qbvnbzoynroxc4t/iphod_spe.corpus?dl=1'
        self.corpus_load_prog_bar = Progressbar(self, mode='indeterminate')
        self.corpus_load_prog_bar.grid()
        self.corpus_load_prog_bar.start()
        if not os.path.exists(path):
            self.corpus_download_thread = ThreadedTask(None,
                                target=self.process_download_corpus_queue,
                                args=(download_link,path))
            self.corpus_download_thread.start()



    def process_download_corpus_queue(self,download_link,path):
        filename,headers = urlretrieve(download_link,path)
        self.corpus_load_prog_bar.stop()
        self.destroy()

class CorpusFromTextWindow(Toplevel):
    def __init__(self,master=None, **options):
        super(CorpusFromTextWindow, self).__init__(master=master, **options)
        #Corpus from text variables
        self.punc_vars = [IntVar() for mark in string.punctuation]
        self.new_corpus_string_type = StringVar()
        self.new_corpus_feature_system_var = StringVar()
        self.corpus_from_text_source_file = StringVar()
        self.corpus_from_text_corpus_name_var = StringVar()
        self.corpus_from_text_output_file = StringVar()

        self.title('Create corpus')
        from_text_frame = LabelFrame(self, text='Create corpus from text')

        load_file_frame = Frame(from_text_frame)
        find_file = Button(load_file_frame, text='Select a source text file to create the corpus from', command=self.navigate_to_text)
        find_file.grid(sticky=W)
        from_text_label = Label(load_file_frame, textvariable=self.corpus_from_text_source_file)
        from_text_label.grid(sticky=W)
        load_file_frame.grid(sticky=W)

        from_text_frame.grid()

        punc_frame = LabelFrame(from_text_frame, text='Select punctuation to ignore')
        row = 0
        col = 0
        colmax = 10
        for mark,var in zip(string.punctuation, self.punc_vars):
            check_button = Checkbutton(punc_frame, text=mark, variable=var)
            check_button.grid(row=row, column=col)
            col += 1
            if col > colmax:
                col = 0
                row += 1
        row += 1
        select_frame = Frame(punc_frame)
        select_all = Button(select_frame, text='Select all', command=lambda x=1: [var.set(x) for var in self.punc_vars])
        select_all.grid(row=0,column=0)
        deselect_all = Button(select_frame, text='Deselect all', command=lambda x=0: [var.set(x) for var in self.punc_vars])
        deselect_all.grid(row=0, column=1)
        select_frame.grid(row=row,column=0)
        punc_frame.grid(sticky=W)
        string_type_frame = LabelFrame(from_text_frame, text='Spelling or transcription')
        spelling_only = Radiobutton(string_type_frame, text='Corpus uses orthography',
                            value='spelling', variable=self.new_corpus_string_type)
        spelling_only.grid()
        spelling_only.invoke()
        trans_only = Radiobutton(string_type_frame, text='Corpus uses transcription',
                            value='transcription', variable=self.new_corpus_string_type)
        trans_only.grid()
        #both = Radiobutton(string_type_frame, text='Corpus has both spelling and transcription', value='both', variable=self.from_corpus_string_type)
        #both.grid()
        new_corpus_feature_frame = LabelFrame(string_type_frame, text='Feature system to use (if transcription exists)')

        trans_dir = os.path.join(config['storage']['directory'],'TRANS')
        trans = [x.split('.')[0] for x in os.listdir(trans_dir) if '2' not in x]
        new_corpus_feature_system = OptionMenu(
            new_corpus_feature_frame,#parent
            self.new_corpus_feature_system_var,#variable
            'spe',#selected option,
            *trans)#options in drop-down
        new_corpus_feature_system.grid()
        new_corpus_feature_frame.grid(sticky=W)
        string_type_frame.grid(sticky=W)
        ok_button = Button(from_text_frame, text='Create corpus', command=self.parse_text)
        cancel_button = Button(from_text_frame, text='Cancel', command=self.destroy)
        ok_button.grid()
        cancel_button.grid()
        from_text_frame.grid()

    def navigate_to_text(self):
        text_file = FileDialog.askopenfilename(filetypes=(('Text files', '*.txt'),('Corpus files', '*.corpus')))
        if text_file:
            self.corpus_from_text_source_file.set(text_file)

    def parse_text(self, delimiter=' '):
        source_path = self.corpus_from_text_source_file.get()
        if not os.path.isfile(source_path):
            MessageBox.showerror(message='Cannot find the source file. Double check the path is correct.')
            return

        string_type = self.new_corpus_string_type.get()
        word_count = collections.defaultdict(int)
        ignore_list = list()
        for mark,var in zip(string.punctuation, self.punc_vars):
            if var.get() == 1:
                ignore_list.append(mark)

        with open(source_path, encoding='utf-8', mode='r') as f:
            for line in f.readlines():
                if not line or line == '\n':
                    continue
                line = line.split(delimiter)
                for word in line:
                    word = word.strip()
                    word = [letter for letter in word if not letter in ignore_list]
                    if not word:
                        continue
                    if string_type == 'transcription':
                        word = '.'.join(word)
                    elif string_type == 'spelling':
                        word = ''.join(word)
                    word_count[word] += 1

        total_words = sum(word_count.values())
        corpus_name = os.path.split(source_path)[-1].split('.')[0]
        corpus = Corpus(corpus_name)
        corpus.specifier = FeatureSpecifier(encoding=self.new_corpus_feature_system_var.get())
        segs_list = list(corpus.specifier.matrix.keys())
        transcription_errors = collections.defaultdict(list)
        headers = [string_type,'Frequency','Relative frequency']
        for w,freq in sorted(word_count.items()):
            line = [w,freq,freq/total_words]
            d = {attribute:value for attribute,value in zip(headers,line)}
            word = Word(**d)
            if word.transcription:
                #transcriptions can have phonetic symbol delimiters which is a period
                word.transcription = word.transcription.split('.')
                if len(word.transcription) == 1: #the split didn't work, there's no delimiters
                    word.transcription = list(word.transcription[0])
                if not word.spelling:
                    word.spelling = ''.join(word.transcription)
                try:
                    word._specify_features(self.corpus_factory)
                    word.set_string('transcription')
                except KeyError as e:
                    transcription_errors[str(e)].append(str(word))
                    continue
            corpus.add_word(word)
        corpus.custom = True

        with open(os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus'), 'wb') as f:
            pickle.dump(corpus,f)

        self.destroy()

class CustomCorpusWindow(Toplevel):
    def __init__(self,master=None, **options):
        super(CustomCorpusWindow, self).__init__(master=master, **options)
        self.new_corpus_feature_system_var = StringVar()
        self.corpus_factory = CorpusFactory()
        self.title('Load new corpus')
        custom_corpus_load_frame = LabelFrame(self, text='Corpus information')
        custom_corpus_load_frame.grid()
        corpus_path_label = Label(custom_corpus_load_frame, text='Path to corpus')
        corpus_path_label.grid()
        self.custom_corpus_path = Entry(custom_corpus_load_frame)
        self.custom_corpus_path.grid()
        select_corpus_button = Button(custom_corpus_load_frame, text='Choose file...', command=self.navigate_to_corpus_file)
        select_corpus_button.grid()
        corpus_name_label = Label(custom_corpus_load_frame, text='Name for corpus (auto-suggested)')
        corpus_name_label.grid()
        self.custom_corpus_name = Entry(custom_corpus_load_frame)
        self.custom_corpus_name.grid()
        delimiter_label = Label(custom_corpus_load_frame, text='Delimiter (enter \'t\' for tab)')
        delimiter_label.grid()
        self.delimiter_entry = Entry(custom_corpus_load_frame)
        self.delimiter_entry.delete(0,END)
        self.delimiter_entry.insert(0,',')
        self.delimiter_entry.grid()
        trans_dir = os.path.join(config['storage']['directory'],'TRANS')
        all_feature_systems = [x.split('.')[0] for x in os.listdir(trans_dir) if '2' not in x]
        new_corpus_feature_frame = LabelFrame(custom_corpus_load_frame, text='Feature system to use (if transcription exists)')
        new_corpus_feature_system = OptionMenu(new_corpus_feature_frame,#parent
            self.new_corpus_feature_system_var,#variable
            'spe',#selected option,
            *[fs for fs in all_feature_systems])#options in drop-down
        new_corpus_feature_system.grid()
        new_corpus_feature_frame.grid(sticky=W)
        ok_button = Button(self, text='OK', command=self.confirm_custom_corpus_selection)
        cancel_button = Button(self, text='Cancel', command=self.destroy)
        ok_button.grid()
        cancel_button.grid()
        self.focus()

    def navigate_to_corpus_file(self):
        custom_corpus_filename = FileDialog.askopenfilename(filetypes=(('Text files', '*.txt'),('Corpus files', '*.corpus')))
        if custom_corpus_filename:
            self.custom_corpus_path.delete(0,END)
            self.custom_corpus_path.insert(0, custom_corpus_filename)
            self.custom_corpus_name.delete(0,END)
            suggestion = os.path.basename(custom_corpus_filename).split('.')[0]
            self.custom_corpus_name.insert(0,suggestion)

    def confirm_custom_corpus_selection(self):
        filename = self.custom_corpus_path.get()
        if not os.path.exists(filename):
            MessageBox.showerror(message='Corpus file could not be located. Please verify the path and file name.')

        delimiter = self.delimiter_entry.get()
        corpus_name = self.custom_corpus_name.get()
        if corpus_name in get_corpora_list():
            carry_on = MessageBox.askyesno(message=(
                'A corpus already exists with this name.  Would you like to overwrite it?'))
            if not carry_on:
                return
        if (not filename) or (not delimiter) or (not corpus_name):
            MessageBox.showerror(message='Information is missing. Please verify that you entered something in all the text boxes')
            return
        if delimiter == 't':
            delimiter = '\t'
        self.create_custom_corpus(corpus_name, filename, delimiter)
        self.warn_about_changes = False


    def custom_corpus_worker_thread(self, corpus_name, filename, delimiter):
        with open(filename, encoding='utf-8') as f:
            headers = f.readline()
            headers = headers.split(delimiter)
            if len(headers)==1:
                #delimiter is incorrect
                MessageBox.showerror(message='Could not parse the corpus.\nCheck that the delimiter you typed in matches the one used in the file.')
                return

            headers = [h.strip() for h in headers]
            headers[0] = headers[0].strip('\ufeff')
            if 'feature_system' in headers[-1]:
                feature_system = headers[-1].split('=')[1]
                headers = headers[0:len(headers)-1]
            elif self.new_corpus_feature_system_var.get():
                feature_system = self.new_corpus_feature_system_var.get()
            else:
                feature_system = 'spe'#default

            corpus = Corpus(corpus_name)
            self.corpus_factory.specifier = FeatureSpecifier(encoding=feature_system)
            segs_list = list(self.corpus_factory.specifier.matrix.keys())
            transcription_errors = collections.defaultdict(list)
            for line in f:
                line = line.strip()
                if not line: #blank or just a newline
                    continue
                d = {attribute:value.strip() for attribute,value in zip(headers,line.split(delimiter))}
                word = Word(**d)
                if word.transcription:
                    #transcriptions can have phonetic symbol delimiters which is a period
                    word.transcription = word.transcription.split('.')
                    if len(word.transcription) == 1: #the split didn't work, there's no delimiters
                        word.transcription = list(word.transcription[0])
                    if not word.spelling:
                        word.spelling = ''.join(word.transcription)
                    try:
                        word._specify_features(self.corpus_factory)
                        word.set_string('transcription')
                    except KeyError as e:
                        transcription_errors[str(e)].append(str(word))
                        continue

                corpus.add_word(word)
        
        corpus.specifier = FeatureSpecifier(encoding=feature_system)
        corpus.custom = True
        self.finalize_corpus(corpus, transcription_errors)
        with open(os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus'), 'wb') as f:
            pickle.dump(corpus,f)
        self.destroy()



    def create_custom_corpus(self, corpus_name, filename, delimiter):

        try:
            with open(filename, 'rb') as f:
                corpus = pickle.load(f)
            corpus.custom = True
            self.finalize_corpus(corpus)
            return
        except (pickle.UnpicklingError, ValueError):
            pass

        self.custom_corpus_load_prog_bar = Progressbar(self, mode='indeterminate')
        #this progbar is indeterminate because we can't know how big the custom corpus will be
        self.custom_corpus_load_prog_bar.grid()
        self.custom_corpus_load_prog_bar.start()
        self.custom_corpus_load_thread = ThreadedTask(queue.Queue(),
                                target=self.custom_corpus_worker_thread,
                                args=(corpus_name, filename, delimiter))
        self.custom_corpus_load_thread.start()

    def finalize_corpus(self, corpus, transcription_errors=None):
        self.corpus = corpus
        self.feature_system = corpus.specifier.feature_system
        if transcription_errors:
            filename = 'error_{}_{}.txt'.format(self.new_corpus_feature_system_var.get(), self.corpus.name)
            with open(os.path.join(ERROR_DIR,filename), encoding='utf-8', mode='w') as f:
                print('Some words in your corpus contain symbols that have no match in the \'{}\' feature system you\'ve selected.\r\n'.format(self.new_corpus_feature_system_var.get()),file=f)
                print('To fix this problem, open the features file in a text editor and add the missing symbols and appropriate feature specifications\r\n', file=f)
                print('All feature files are (or should be!) located in the TRANS folder. If you have your own feature file, just drop it into that folder before loading CorpusTools.\r\n', file=f)
                print('The following segments could not be represented:\r\n',file=f)
                for key in sorted(list(transcription_errors.keys())):
                    words = sorted(transcription_errors[key])
                    words = ','.join(words)
                    sep = '\r\n\n'
                    print('Symbol: {}\r\nWords: {}\r\n{}'.format(key,words,sep), file=f)
            msg1 = 'Not every symbol in your corpus can be interpreted with this feature system.'
            msg2 = 'A file called {} has been placed in your ERRORS folder ({}) explaining this problem in more detail.'.format(
            filename,ERROR_DIR)
            msg3 = 'Words with interpretable symbols will still be displayed. Consult the output file above to see how to fix this problem.'
            msg = '\n'.join([msg1, msg2, msg3])
            MessageBox.showwarning(message=msg)


class CorpusManager(object):
    def __init__(self,master=None, **options):
        self.top = Toplevel()
        self.top.title('Load corpus')
        self.corpus = None
        corpus_frame = Frame(self.top)
        self.available_corpora = Listbox(corpus_frame)
        self.get_available_corpora()
        self.available_corpora.grid(row=0,column=0)
        self.available_trans = Listbox(corpus_frame)
        self.get_available_trans()
        self.available_trans.grid(row=0,column=1)
        corpus_frame.grid(row=0,column=0)
        button_frame = Frame(self.top)
        load_button = Button(button_frame,
                                        text='Load selected corpus',
                                        command=self.load_corpus)
        load_button.grid()
        download_button = Button(button_frame,
                                        text='Download example corpora',
                                        command=self.download_corpus)
        download_button.grid()
        load_from_txt_button = Button(button_frame,
                                        text='Load corpus from text file',
                                        command=self.load_corpus_from_txt)
        load_from_txt_button.grid()
        create_from_text_button = Button(button_frame,
                                    text='Create corpus from text file',
                                    command=self.create_corpus_from_text)
        create_from_text_button.grid()
        button_frame.grid(row=0,column=1)


    def load_corpus(self):
        try:
            corpus_name = self.available_corpora.get(self.available_corpora.curselection())
            path = os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus')
            with open(path, 'rb') as f:
                self.corpus = pickle.load(f)
            self.top.destroy()
        except TclError:
            pass

    def get_corpus(self):
        return self.corpus


    def get_available_trans(self):
        trans_dir = os.path.join(config['storage']['directory'],'TRANS')
        trans = [x.split('.')[0] for x in os.listdir(trans_dir) if '2' not in x]
        self.available_trans.delete(0,END)
        for t in trans:
            self.available_trans.insert(END,t)

    def get_available_corpora(self):
        corpora = get_corpora_list()
        self.available_corpora.delete(0,END)
        for c in corpora:
            self.available_corpora.insert(END,c)


    def download_corpus(self):
        download = DownloadWindow()
        download.wait_window()
        self.get_available_corpora()

    def load_corpus_from_txt(self):
        custom = CustomCorpusWindow()
        custom.wait_window()
        self.get_available_corpora()

    def create_corpus_from_text(self):
        from_text_window = CorpusFromTextWindow()
        from_text_window.wait_window()
        self.get_available_corpora()






