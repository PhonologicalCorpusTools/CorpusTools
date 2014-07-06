
import os
import pickle
import collections

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton, 
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE, Toplevel, Listbox, OptionMenu )
from tkinter.ttk import Progressbar
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

from urllib.request import urlretrieve
import queue

from corpustools.corpus.classes import (CorpusFactory, Corpus, FeatureSpecifier,
                                    Word, Segment)
from corpustools.gui.basegui import (AboutWindow, FunctionWindow, 
                    ResultsWindow, MultiListbox, ThreadedTask, config, ERROR_DIR)

class DownloadWindow(Toplevel):
    def __init__(self,master=None, **options):
        super(DownloadWindow, self).__init__(master=master, **options)
        self.corpus_button_var = StringVar()
        self.corpusq = queue.Queue()
        self.title('Download corpora')
        corpus_frame = Frame(self)
        corpus_area = LabelFrame(corpus_frame, text='Select a corpus')
        corpus_area.grid(sticky=W, column=0, row=0)
        subtlex_button = Radiobutton(corpus_area, text='Toy', variable=self.corpus_button_var, value='toy')
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
        if corpus_name == 'toy':
            download_link = ''
        elif corpus_name == 'iphod':
            download_link = 'https://www.dropbox.com/s/qbvnbzoynroxc4t/iphod_spe.corpus?dl=1'
        self.corpus_load_prog_bar = Progressbar(self, mode='indeterminate')
        self.corpus_load_prog_bar.grid()
        self.corpus_load_prog_bar.start()
        path = os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus')
        if not os.path.exists(path):
            self.corpus_download_thread = ThreadedTask(None,
                                target=self.process_download_corpus_queue,
                                args=(download_link,path))
            self.corpus_download_thread.start()
            
            

    def process_download_corpus_queue(self,download_link,path):
        filename,headers = urlretrieve(download_link,path)
        self.corpus_load_prog_bar.stop()
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
        if (not filename) or (not delimiter) or (not corpus_name):
            MessageBox.showerror(message='Information is missing. Please verify that you entered something in all the text boxes')
            return
        if delimiter == 't':
            delimiter = '\t'
        self.create_custom_corpus(corpus_name, filename, delimiter)
        self.warn_about_changes = False 
        
    def process_custom_corpus_queue(self):
        try:
            msg = self.q.get(0)
            if msg == -99:
                self.custom_corpus_load_prog_bar.stop()
                transcription_errors = self.corpusq.get()
                corpus = self.corpusq.get()
                self.finalize_corpus(corpus, transcription_errors)
                self.destroy()
            else:
                self.custom_corpus_load_prog_bar.step()
                #self.master.after(100, self.process_queue)
                self.after(3, self.process_custom_corpus_queue)
        except queue.Empty:
            #queue is empty initially for a while because it takes some time for the
            #corpus_factory.make_corpus to actually start producing worsd
            self.after(10, self.process_custom_corpus_queue)

    def custom_corpus_worker_thread(self, corpus_name, filename, delimiter, queue, corpusq):
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
                queue.put(1)
        queue.put(-99)#flag
        corpus.orthography.extend([letter for letter in word.spelling if not letter in corpus.orthography])
        random_word = corpus.random_word()
        if random_word.transcription is not None:
            corpus.inventory.extend([seg for seg in word.transcription if not seg in corpus.inventory])
        else:
            corpus.inventory = list()
        corpus.orthography.append('#')
        corpus.inventory.append(Segment('#'))
        corpus.specifier = FeatureSpecifier(encoding=feature_system)
        corpus.custom = True
        with open(os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus'), 'wb') as f:
            pickle.dump(corpus,f)
        corpusq.put(transcription_errors)
        corpusq.put(corpus)
            
        

    def create_custom_corpus(self, corpus_name, filename, delimiter):

        try:
            with open(filename, 'rb') as f:
                corpus = pickle.load(f)
            corpus.custom = True
            self.finalize_corpus(corpus)
            return
        except (pickle.UnpicklingError, ValueError):
            pass

        self.q = queue.Queue()
        self.corpusq = queue.Queue(1)
        self.custom_corpus_load_prog_bar = Progressbar(self, mode='indeterminate')
        #this progbar is indeterminate because we can't know how big the custom corpus will be
        self.custom_corpus_load_prog_bar.grid()
        self.custom_corpus_load_thread = ThreadedTask(self.q,
                                target=self.custom_corpus_worker_thread,
                                args=(corpus_name, filename, delimiter, self.q, self.corpusq))
        self.custom_corpus_load_thread.start()
        self.process_custom_corpus_queue()

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


class LoadCorpusWindow(Toplevel):
    def __init__(self,master=None, **options):
        super(LoadCorpusWindow, self).__init__(master=master, **options)
        self.title('Load corpus')
        self.corpus = None
        corpus_frame = Frame(self)
        self.available_corpora = Listbox(corpus_frame)
        self.get_available_corpora()
        self.available_corpora.grid(row=0,column=0)
        self.available_trans = Listbox(corpus_frame)
        self.get_available_trans()
        self.available_trans.grid(row=0,column=1)
        button_frame = Frame(self)
        load_button = Button(button_frame, text='Load selected corpus', command=self.load_corpus)
        load_button.grid()
        download_button = Button(button_frame, text='Download example corpora', command=self.download_corpus)
        download_button.grid()
        load_from_txt_button = Button(button_frame, text='Load corpus from text file', command=self.load_corpus_from_txt)
        load_from_txt_button.grid()
        create_from_txt_button = Button(button_frame, text='Create corpus from text file', command=self.create_corpus_from_text)
        create_from_txt_button.grid()
        button_frame.grid(row=1,column=1)
        
        corpus_frame.grid()
        
    def load_corpus(self):
        try:
            corpus_name = self.available_corpora.get(self.available_corpora.curselection())
            path = os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus')
            with open(path, 'rb') as f:
                self.corpus = pickle.load(f)
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
        corpus_dir = os.path.join(config['storage']['directory'],'CORPUS')
        corpora = [x.split('.')[0] for x in os.listdir(corpus_dir)]
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
        pass
        
    def choose_custom_corpus(self, event=None):

        self.custom_corpus_load_screen = Toplevel()
        self.custom_corpus_load_screen.title('Load custom corpus')
        


    def navigate_to_text(self):
        text_file = FileDialog.askopenfilename(filetypes=(('Text files', '*.txt'),('Corpus files', '*.corpus')))
        if text_file:
            self.corpus_from_text_source_file.set(text_file)
    def corpus_from_text(self):

        self.from_text_window = Toplevel()
        self.from_text_window.title('Create corpus')
        from_text_frame = LabelFrame(self.from_text_window, text='Create corpus from text')

        load_file_frame = Frame(from_text_frame)
        find_file = Button(load_file_frame, text='Select a source text file to create the corpus from', command=self.navigate_to_text)
        find_file.grid(sticky=W)
        from_text_label = Label(load_file_frame, textvariable=self.corpus_from_text_source_file)
        from_text_label.grid(sticky=W)
        load_file_frame.grid(sticky=W)

        save_file_frame = Frame(from_text_frame)
        save_button = Button(save_file_frame, text='Select save location for new corpus', command=self.suggest_corpus_from_text_name)
        save_button.grid(sticky=W)
        save_location = Label(save_file_frame, textvariable=self.corpus_from_text_output_file)
        save_location.grid(sticky=W)
        save_file_frame.grid(sticky=W)
        from_text_frame.grid()
##        new_name_frame = LabelFrame(from_text_frame, text='New corpus name and save location')
##        name_label = Label(new_name_frame, text='Name for new corpus:')
##        name_label.grid(row=0,column=0,sticky=W)
##        self.new_name_entry = Entry(new_name_frame)
##        self.new_name_entry.grid(row=0,column=1,sticky=W)
##        new_name_frame.grid(sticky=W)

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
        new_corpus_feature_system = OptionMenu(
            new_corpus_feature_frame,#parent
            self.new_corpus_feature_system_var,#variable
            'spe',#selected option,
            *[fs for fs in self.all_feature_systems])#options in drop-down
        new_corpus_feature_system.grid()
        new_corpus_feature_frame.grid(sticky=W)
        string_type_frame.grid(sticky=W)
        ok_button = Button(from_text_frame, text='Create corpus', command=self.parse_text)
        cancel_button = Button(from_text_frame, text='Cancel', command=self.from_text_window.destroy)
        ok_button.grid()
        cancel_button.grid()
        from_text_frame.grid()

    def parse_text(self, delimiter=' '):

        if not os.path.isfile(self.corpus_from_text_source_file.get()):
            MessageBox.showerror(message='Cannot find the source file. Double check the path is correct.')
            return

        if not self.corpus_from_text_output_file.get():
            MessageBox.showerror(message='Please select a location for the output file.')
            return

        string_type = self.new_corpus_string_type.get()
        word_count = collections.defaultdict(int)
        ignore_list = list()
        for mark,var in zip(string.punctuation, self.punc_vars):
            if var.get() == 1:
                ignore_list.append(mark)

        with open(self.corpus_from_text_source_file.get(), encoding='utf-8', mode='r') as f:
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
        outputfile = self.corpus_from_text_output_file.get()

        with open(outputfile, encoding='utf-8', mode='w') as f:
            print('{},Frequency,Relative frequency,feature_system={}\r'.format(
                string_type,self.new_corpus_feature_system_var.get()), file=f)
            for word,freq in sorted(word_count.items()):
                print('{},{},{}\r'.format(word,freq,freq/total_words),file=f)

        self.warn_about_changes = False
        MessageBox.showinfo(message='Corpus created! You can open it from Corpus > Use custom corpus...')
        if open_corpus:
            self.load_corpus
        self.from_text_window.destroy()

    def choose_corpus(self,event=None):
        #This is always called from a menu
        self.corpus_select_screen = Toplevel()

        


    def process_load_corpus_queue(self):
        try:
            self.corpus = self.corpusq.get()
            self.corpus_load_prog_bar.stop()
            #self.corpus_load_prog_bar.destroy()
            self.corpus_select_screen.destroy()
            self.main_screen_refresh()
            return
        except queue.Empty:
            #queue is empty initially for a while because it takes some time for the
            #corpus_factory.make_corpus to actually start producing words
            self.corpus_select_screen.after(5, self.process_load_corpus_queue)

    def load_corpus2(self, corpus_name, features_name, size=10000):
        """
        good if size is fixed low for testing purposes, the actual program would probably want
        to load the entire corpus every time
        """
        if corpus_name == 'iphod':
            if features_name == 'spe':
                path = os.path.join(self.corpus_dir, 'iphod_spe.corpus')
                download_link = 'https://www.dropbox.com/s/c6v6tij5phacujl/iphod_spe.corpus?dl=1'
            elif features_name == 'hayes':
                path = os.path.join(self.corpus_dir, 'iphod_hayes.corpus')
                download_link = 'https://www.dropbox.com/s/zs5p0l26ett17iy/iphod_hayes.corpus?dl=1'
        elif corpus_name == 'subtlex':
            if features_name == 'spe':
                path = os.path.join(self.corpus_dir, 'subtlex_spe.corpus')
            elif features_name == 'hayes':
                path = os.path.join(self.corpus_dir, 'subtlex_hayes.corpus')
        
        self.corpus_load_prog_bar = Progressbar(self.corpus_select_screen, mode='indeterminate')
        self.corpus_load_prog_bar.grid()
        self.corpus_load_prog_bar.start()
        
        if not os.path.exists(path) and corpus_name == 'iphod':
            #import requests
            #with open(path, 'wb') as handle:
                #response = requests.get(download_link, stream=True)

                ##if not response.ok:
                    ## Something went wrong

                #for block in response.iter_content(1024):

                    #handle.write(block)
            from urllib.request import urlretrieve
            filename,headers = urlretrieve(download_link,path)
        elif not os.path.exists(path):
            return
        with open(path, 'rb') as f:
            corpus = pickle.load(f)
        corpus.custom = False
        self.finalize_corpus(corpus)
        self.corpus_select_screen.destroy()
        self.main_screen_refresh()
        return

##        self.corpus_load_thread = ThreadedTask(self.corpusq,
##                        target=pickle.load,
##                        args=(f,))
##        self.corpus_load_thread.start()
##        self.process_load_corpus_queue()

##
##
##        #pre-computed size variables1
##        if size == 'all':
##            if corpus_name == 'iphod':
##                size = 54030
##            elif corpus_name == 'subtlex':
##                size = 48212
##        self.q = queue.Queue()
##        self.corpus_load_prog_bar = Progressbar(self.corpus_select_screen, mode='determinate', maximum=size)
##        self.corpus_load_prog_bar.grid()
##        #self.corpus_load_prog_bar.start()
##        self.corpus_load_thread = ThreadedTask(self.q,
##                                target=self.corpus_factory.make_corpus_from_gui,
##                                args=(corpus_name, features_name, size, self.q, self.corpusq),
##                                )
##        self.corpus_load_thread.start()
##        self.process_queue()



        
