import os
import collections

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE, Toplevel, Listbox, OptionMenu, IntVar, Checkbutton, E, N, S )
from tkinter.ttk import Progressbar
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue
import string

from corpustools.corpus.io import (download_binary, save_binary, load_binary,
                                    load_corpus_csv,load_corpus_text,
                                    export_corpus_csv, export_feature_matrix_csv,
                                    load_feature_matrix_csv,DelimiterError)
from corpustools.gui.basegui import (AboutWindow, FunctionWindow,
                    ResultsWindow, TableView, ThreadedTask, config, ERROR_DIR)

def get_corpora_list():
    corpus_dir = os.path.join(config['storage']['directory'],'CORPUS')
    corpora = [x.split('.')[0] for x in os.listdir(corpus_dir)]
    return corpora
    
def get_systems_list():
    system_dir = os.path.join(config['storage']['directory'],'FEATURE')
    systems = [x.split('.')[0] for x in os.listdir(system_dir)]
    return systems

class DownloadCorpusWindow(Toplevel):
    """
    Window for downloading corpora
    """
    def __init__(self,master=None, **options):
        super(DownloadCorpusWindow, self).__init__(master=master, **options)
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
                'This corpus is already available locally. Would you like to redownload it?'))
            if not carry_on:
                return
            os.remove(path)
        self.corpus_load_prog_bar = Progressbar(self, mode='indeterminate')
        self.corpus_load_prog_bar.grid()
        self.corpus_load_prog_bar.start()
        if not os.path.exists(path):
            self.corpus_download_thread = ThreadedTask(None,
                                target=self.download_corpus,
                                args=(corpus_name,path))
            self.corpus_download_thread.start()



    def download_corpus(self,corpus_name,path):
        download_binary(corpus_name,path)
        self.corpus_load_prog_bar.stop()
        self.destroy()

class CorpusFromTextWindow(Toplevel):
    """
    Window for generating a corpus from a file of running text
    """
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
        new_corpus_feature_frame = LabelFrame(self, text='Feature system to use (if transcription exists)')

        available_systems = ['']+get_systems_list()
        new_corpus_feature_system = OptionMenu(
            new_corpus_feature_frame,#parent
            self.new_corpus_feature_system_var,#variable
            *available_systems)#options in drop-down
        new_corpus_feature_system.grid()
        new_corpus_feature_frame.grid(sticky=W)
        string_type_frame.grid(sticky=W)
        delim_frame = LabelFrame(from_text_frame, text='Delimiters')
        delimiter_label = Label(delim_frame, text='Word delimiter (defaults to space)')
        delimiter_label.grid()
        self.delimiter_entry = Entry(delim_frame)
        self.delimiter_entry.delete(0,END)
        self.delimiter_entry.insert(0,' ')
        self.delimiter_entry.grid()
        trans_delimiter_label = Label(delim_frame, text='Transcription delimiter (No character means every symbol\n will be interpreted as a segment)')
        trans_delimiter_label.grid()
        self.trans_delimiter_entry = Entry(delim_frame)
        self.trans_delimiter_entry.delete(0,END)
        self.trans_delimiter_entry.insert(0,'.')
        self.trans_delimiter_entry.grid()
        delim_frame.grid(sticky=E)
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

        string_type = self.new_corpus_string_type.get()
        ignore_list = list()
        for mark,var in zip(string.punctuation, self.punc_vars):
            if var.get() == 1:
                ignore_list.append(mark)

        delimiter = self.delimiter_entry.get()
        trans_delimiter = self.trans_delimiter_entry.get()
        
        if trans_delimiter in ignore_list:
            MessageBox.showerror(message='Transcription delimiter is currently set to being ignored,')
            return

        corpus_name = os.path.split(source_path)[-1].split('.')[0]
        feature_system = self.new_corpus_feature_system_var.get()
        if feature_system:
            feature_system = os.path.join(config['storage']['directory'],
                                                'FEATURE',
                                                feature_system+'.feature')

        corpus,transcription_errors = load_corpus_text(corpus_name,source_path,delimiter,ignore_list,trans_delimiter,feature_system,string_type)
        self.finalize_corpus(corpus,transcription_errors)
        save_binary(corpus, os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus'))
        
        self.destroy()


    def finalize_corpus(self, corpus, transcription_errors=None):
        self.corpus = corpus
        if transcription_errors:
            not_found = sorted(list(transcription_errors.keys()))
            msg1 = 'Not every symbol in your corpus can be interpreted with this feature system.'
            msg2 = 'The symbols that were missing were {}.\n'.format(', '.join(not_found))
            msg3 = 'Would you like to create all of them as unspecified? You can edit them later by going to Options-> View/change feature system...\nYou can also manually create the segments in there.'
            msg = '\n'.join([msg1, msg2, msg3])
            carry_on = MessageBox.askyesno(message=msg)
            if not carry_on:
                return
            for s in not_found:
                self.corpus.get_feature_matrix().add_segment(s.strip('\''),{})
            self.corpus.get_feature_matrix().validate()

class CustomCorpusWindow(Toplevel):
    """
    Window for parsing a column-delimited text file into a Corpus
    """
    def __init__(self,master=None, **options):
        super(CustomCorpusWindow, self).__init__(master=master, **options)
        self.new_corpus_feature_system_var = StringVar()
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
        delimiter_label = Label(custom_corpus_load_frame, text='Column delimiter (enter \'t\' for tab)')
        delimiter_label.grid()
        self.delimiter_entry = Entry(custom_corpus_load_frame)
        self.delimiter_entry.delete(0,END)
        self.delimiter_entry.insert(0,',')
        self.delimiter_entry.grid()
        trans_delimiter_label = Label(custom_corpus_load_frame, text='Transcription delimiter (No character means every symbol\n will be interpreted as a segment)')
        trans_delimiter_label.grid()
        self.trans_delimiter_entry = Entry(custom_corpus_load_frame)
        self.trans_delimiter_entry.delete(0,END)
        self.trans_delimiter_entry.insert(0,'.')
        self.trans_delimiter_entry.grid()
        available_systems = ['']+get_systems_list()
        new_corpus_feature_frame = LabelFrame(custom_corpus_load_frame, text='Feature system to use (if transcription exists)')
        new_corpus_feature_system = OptionMenu(new_corpus_feature_frame,#parent
            self.new_corpus_feature_system_var,#variable
            *available_systems)#options in drop-down
        new_corpus_feature_system.grid()
        new_corpus_feature_frame.grid(sticky=W)
        ok_button = Button(self, text='OK', command=self.confirm_custom_corpus_selection)
        cancel_button = Button(self, text='Cancel', command=self.destroy)
        ok_button.grid()
        cancel_button.grid()
        self.focus()

    def navigate_to_corpus_file(self):
        custom_corpus_filename = FileDialog.askopenfilename(filetypes=(('Text files', '*.txt'),('CSV files', '*.csv')))
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
        trans_delimiter = self.trans_delimiter_entry.get()
        corpus_name = self.custom_corpus_name.get()
        if corpus_name in get_corpora_list():
            carry_on = MessageBox.askyesno(message=(
                'A corpus already exists with this name. Would you like to overwrite it?'))
            if not carry_on:
                return
        if (not filename) or (not delimiter) or (not corpus_name):
            MessageBox.showerror(message='Information is missing. Please verify that you entered something in all the text boxes')
            return
            
        if delimiter == 't':
            delimiter = '\t'
        if delimiter == trans_delimiter:
            MessageBox.showerror(message='Delimiter for columns matches delimiter for transcriptions. Please ensure that these are different.')
            return
        self.create_custom_corpus(corpus_name, filename, delimiter, trans_delimiter)

    def create_custom_corpus(self, corpus_name, filename, delimiter, trans_delimiter):

        self.custom_corpus_load_prog_bar = Progressbar(self, mode='indeterminate')
        #this progbar is indeterminate because we can't know how big the custom corpus will be
        self.custom_corpus_load_prog_bar.grid()
        self.custom_corpus_load_prog_bar.start()
        self.custom_corpus_load_thread = ThreadedTask(queue.Queue(),
                                target=self.custom_corpus_thread,
                                args=(corpus_name, filename, delimiter, trans_delimiter))
        self.custom_corpus_load_thread.start()

    def custom_corpus_thread(self, corpus_name, filename, delimiter, trans_delimiter):
        feature_system = self.new_corpus_feature_system_var.get()
        if feature_system:
            feature_system = os.path.join(config['storage']['directory'],
                                                'FEATURE',
                                                feature_system+'.feature')
        try:
            corpus, errors = load_corpus_csv(corpus_name, filename, delimiter, trans_delimiter,feature_system)
        except DelimiterError:
            
            #delimiter is incorrect
            MessageBox.showerror(message='Could not parse the corpus.\n\Check that the delimiter you typed in matches the one used in the file.')
            return
        self.finalize_corpus(corpus,errors)
        save_binary(corpus,os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus'))
        self.destroy()


    def finalize_corpus(self, corpus, transcription_errors=None):
        self.corpus = corpus
        if transcription_errors:
            not_found = sorted(list(transcription_errors.keys()))
            msg1 = 'Not every symbol in your corpus can be interpreted with this feature system.'
            msg2 = 'The symbols that were missing were {}.\n'.format(', '.join(not_found))
            msg3 = 'Would you like to create all of them as unspecified? You can edit them later by going to Options-> View/change feature system...\nYou can also manually create the segments in there.'
            msg = '\n'.join([msg1, msg2, msg3])
            carry_on = MessageBox.askyesno(message=msg)
            if not carry_on:
                return
            for s in not_found:
                self.corpus.get_feature_matrix().add_segment(s.strip('\''),{})
            self.corpus.get_feature_matrix().validate()


class CorpusManager(object):
    """
    Main window for dealing with corpora
    """
    def __init__(self,master=None, **options):
        self.top = Toplevel()
        self.top.title('Load corpus')
        self.corpus = None
        corpus_frame = LabelFrame(self.top,text='Available corpora')
        self.available_corpora = Listbox(corpus_frame)
        self.get_available_corpora()
        self.available_corpora.grid(row=0,column=0)
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
        remove_button = Button(button_frame,
                                    text='Remove selected corpus',
                                    command=self.remove_corpus)
        remove_button.grid()
        button_frame.grid(row=0,column=1)

    def remove_corpus(self):
        try:
            corpus_name = self.available_corpora.get(self.available_corpora.curselection())
            carry_on = MessageBox.askyesno(message=(
                'This will irreversibly delete the {} corpus.  Are you sure?'.format(corpus_name)))
            if not carry_on:
                return
            os.remove(os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus'))
            self.get_available_corpora()
        except TclError:
            pass

    def load_corpus(self):
        try:
            corpus_name = self.available_corpora.get(self.available_corpora.curselection())
            self.corpus = load_binary(os.path.join(config['storage']['directory'],'CORPUS',corpus_name+'.corpus'))
            self.top.destroy()
        except TclError:
            pass

    def get_corpus(self):
        return self.corpus

    def get_available_corpora(self):
        corpora = get_corpora_list()
        self.available_corpora.delete(0,END)
        for c in corpora:
            self.available_corpora.insert(END,c)


    def download_corpus(self):
        download = DownloadCorpusWindow()
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

class DownloadFeatureMatrixWindow(Toplevel):
    """
    Window for downloading FeatureMatrix binaries
    """
    def __init__(self,master=None, **options):
        super(DownloadFeatureMatrixWindow, self).__init__(master=master, **options)
        self.system_button_var = StringVar()
        self.title('Download feature systems')
        system_frame = Frame(self)
        system_area = LabelFrame(system_frame, text='Select a feature system')
        system_area.grid(sticky=W, column=0, row=0)
        spe_button = Radiobutton(system_area, text='Sound Pattern of English (SPE)', variable=self.system_button_var, value='spe')
        spe_button.grid(sticky=W,row=0)
        spe_button.invoke()#.select() doesn't work on ttk.Button
        hayes_button = Radiobutton(system_area, text='Hayes', variable=self.system_button_var, value='hayes')
        hayes_button.grid(sticky=W,row=1)
        system_frame.grid()

        button_frame = Frame(self)
        ok_button = Button(button_frame,text='OK', command=self.confirm_download)
        ok_button.grid(row=3, column=0)#, sticky=W, padx=3)
        cancel_button = Button(button_frame,text='Cancel', command=self.destroy)
        cancel_button.grid(row = 3, column=1)#, sticky=W, padx=3)
        button_frame.grid()

        warning_label = Label(self, text='Please be patient. It can take up to 30 seconds to download a feature system.')
        warning_label.grid()
        self.focus()

    def confirm_download(self):
        system_name = self.system_button_var.get()
        path = os.path.join(config['storage']['directory'],'FEATURE',system_name+'.feature')
        if system_name in get_systems_list():
            carry_on = MessageBox.askyesno(message=(
                'This system is already available locally. Would you like to redownload it?'))
            if not carry_on:
                return
            os.remove(path)
        self.prog_bar = Progressbar(self, mode='indeterminate')
        self.prog_bar.grid()
        self.prog_bar.start()
        if not os.path.exists(path):
            self.system_download_thread = ThreadedTask(None,
                                target=self.download,
                                args=(system_name,path))
            self.system_download_thread.start()

    def download(self,system_name,path):
        download_binary(system_name,path)
        
        self.prog_bar.stop()
        self.destroy()

class FeatureSystemManager(object):
    """
    Main window for dealing with feature systems
    """
    def __init__(self):
        self.top = Toplevel()
        self.top.title('Manage feature systems')
        self.feature_matrix = None
        systems_frame = LabelFrame(self.top,text='Available feature systems')
        self.available_systems = Listbox(systems_frame)
        self.get_available_systems()
        self.available_systems.grid(row=0,column=1)
        systems_frame.grid(row=0,column=0)
        button_frame = Frame(self.top)
        download_button = Button(button_frame,
                                        text='Download feature systems',
                                        command=self.download)
        download_button.grid()
        create_from_text_button = Button(button_frame,
                                    text='Create feature system from text file',
                                    command=self.create_from_text)
        create_from_text_button.grid()
        remove_button = Button(button_frame,
                                    text='Remove selected feature system',
                                    command=self.remove_system)
        remove_button.grid()
        done_button = Button(button_frame,
                                    text='Done',
                                    command=self.top.destroy)
        done_button.grid()
        button_frame.grid(row=0,column=1)

    def get_available_systems(self):
        systems = get_systems_list()
        self.available_systems.delete(0,END)
        for t in systems:
            self.available_systems.insert(END,t)

    def remove_system(self):
        try:
            name = self.available_systems.get(self.available_systems.curselection())
            carry_on = MessageBox.askyesno(message=(
                'This will irreversibly delete the {} feature system.  Are you sure?'.format(name)))
            if not carry_on:
                return
            os.remove(os.path.join(config['storage']['directory'],'FEATURE',name+'.feature'))
            self.get_available_systems()
        except TclError:
            pass
            
    def download(self):
        download = DownloadFeatureMatrixWindow()
        download.wait_window()
        self.get_available_systems()

    def create_from_text(self):
        custom = CustomFeatureMatrixWindow()
        custom.wait_window()
        self.get_available_systems()

class CustomFeatureMatrixWindow(Toplevel):
    """
    Window for parsing column-delimited feature matrix
    """
    def __init__(self,master=None, **options):
        super(CustomFeatureMatrixWindow, self).__init__(master=master, **options)
        self.title('Import feature system')
        load_frame = LabelFrame(self, text='Feature system information')
        load_frame.grid()
        path_label = Label(load_frame, text='Path to feature matrix')
        path_label.grid()
        self.path_entry = Entry(load_frame)
        self.path_entry.grid()
        select_button = Button(load_frame, text='Choose file...', command=self.navigate_to_file)
        select_button.grid()
        name_label = Label(load_frame, text='Name for corpus (auto-suggested)')
        name_label.grid()
        self.name_entry = Entry(load_frame)
        self.name_entry.grid()
        delimiter_label = Label(load_frame, text='Column delimiter (enter \'t\' for tab)')
        delimiter_label.grid()
        self.delimiter_entry = Entry(load_frame)
        self.delimiter_entry.delete(0,END)
        self.delimiter_entry.insert(0,',')
        self.delimiter_entry.grid()
        ok_button = Button(self, text='OK', command=self.confirm_selection)
        cancel_button = Button(self, text='Cancel', command=self.destroy)
        ok_button.grid()
        cancel_button.grid()
        self.focus()

    def navigate_to_file(self):
        filename = FileDialog.askopenfilename(filetypes=(('Text files', '*.txt'),('Corpus files', '*.corpus')))
        if filename:
            self.path_entry.delete(0,END)
            self.path_entry.insert(0, filename)
            self.name_entry.delete(0,END)
            suggestion = os.path.basename(filename).split('.')[0]
            self.name_entry.insert(0,suggestion)

    def confirm_selection(self):
        filename = self.path_entry.get()
        if not os.path.exists(filename):
            MessageBox.showerror(message='Feature matrix file could not be located. Please verify the path and file name.')

        delimiter = self.delimiter_entry.get()
        system_name = self.name_entry.get()
        if system_name in get_systems_list():
            carry_on = MessageBox.askyesno(message=(
                'A feature system already exists with this name. Would you like to overwrite it?'))
            if not carry_on:
                return
        if (not filename) or (not delimiter) or (not system_name):
            MessageBox.showerror(message='Information is missing. Please verify that you entered something in all the text boxes')
            return
            
        if delimiter == 't':
            delimiter = '\t'
        self.create(system_name, filename, delimiter)


    def create(self, name, filename, delimiter):
        try:
            system = load_feature_matrix_csv(name, filename, delimiter)
        except DelimiterError:
            
            #delimiter is incorrect
            MessageBox.showerror(message='Could not parse the file.\nCheck that the delimiter you typed in matches the one used in the file.')
            return
        except KeyError:
            MessageBox.showerror(message='Could not find a \'symbol\' column.  Please make sure that the segment symbols are in a column named \'symbol\'.')
            return
        save_binary(system,os.path.join(config['storage']['directory'],'FEATURE',name+'.feature'))
        self.destroy()

class EditSegmentWindow(object):
    """
    Window for editing or adding a segment to a feature system 
    """
    def __init__(self,feature_list,possible_values, initial_data = None):
        self.top = Toplevel()
        self.top.title('Add a segment')
        self.commit = False
        self.seg_var = StringVar()
        self.feature_vars = {f: StringVar() for f in feature_list}
        add_frame = Frame(self.top)
        seg_label = Label(add_frame, text='Symbol')
        seg_label.grid(row=0,column=0)
        seg_entry = Entry(add_frame,textvariable=self.seg_var,width=5)
        seg_entry.grid(row=1,column=0)
        #HACK - Should have dynamic scaling of widgets based on size of window
        colmax = 12
        col = 1
        row = 0
        for f, v in self.feature_vars.items():
            label = Label(add_frame, text=f)
            label.grid(row=row,column = col)
            entry = OptionMenu(add_frame,#parent
                                v,#variable
                                *possible_values)
            entry.grid(row=row+1,column = col)
            col+=1
            if col > colmax:
                col = 0
                row += 2
        add_frame.grid()
        
        if initial_data:
            init_seg, init_feats = initial_data
            self.seg_var.set(init_seg)
            for k,v in self.feature_vars.items():
                v.set(init_feats[k])
        else:
            default = ''
            for v in possible_values:
                if v not in ['+','-']:
                    default = v
                    break
            for k,v in self.feature_vars.items():
                v.set(default)
        
        button_frame = Frame(self.top)
        ok_button = Button(button_frame, text='Ok', command=self.confirm_add)
        ok_button.grid(row=1,column=0)
        cancel_button = Button(button_frame, text='Cancel', command=self.top.destroy)
        cancel_button.grid(row=1,column=1)
        button_frame.grid()
        
    def confirm_add(self):
        self.featspec = {f:v.get() for f,v in self.feature_vars.items()}
        self.seg = self.seg_var.get()
        self.commit = True
        self.top.destroy()
        
class AddFeatureWindow(object):
    """
    Window for adding a new feature to a feature system
    """
    def __init__(self,feature_list):
        self.top = Toplevel()
        self.top.title('Add a feature')
        self.commit = False
        self.feature_var = StringVar()
        self.feature_list = feature_list
        add_frame = Frame(self.top)
        seg_label = Label(add_frame, text='Feature name')
        seg_label.grid(row=0,column=0)
        seg_entry = Entry(add_frame,textvariable=self.feature_var)
        seg_entry.grid(row=1,column=0)
        add_frame.grid()
        
        button_frame = Frame(self.top)
        ok_button = Button(button_frame, text='Ok', command=self.confirm_add)
        ok_button.grid(row=1,column=0)
        cancel_button = Button(button_frame, text='Cancel', command=self.top.destroy)
        cancel_button.grid(row=1,column=1)
        button_frame.grid()
        
    def confirm_add(self):
        self.feature = self.feature_var.get()
        if self.feature in self.feature_list:
            MessageBox.showerror(message='A feature already exists with that name.')
            return
        self.commit = True
        self.top.destroy()
        


class EditFeatureSystemWindow(object):
    """
    Window for editing and changing the feature system used by a corpus
    """
    def __init__(self,corpus):
        self.change = False
        self.feature_system_option_menu_var = StringVar()
        self.corpus = corpus
        self.feature_matrix = self.corpus.get_feature_matrix()
        self.top = Toplevel()
        self.top.geometry("%dx%d%+d%+d" % (860,600,250,250))
        self.top.title('Edit feature system')

        self.feature_frame = Frame(self.top)
        self.feature_frame.pack(side='top',expand=True,fill='both')
        
        option_frame = Frame(self.top)
        option_frame.pack()
        change_frame = LabelFrame(option_frame,text='Change feature systems')
        feature_menu = OptionMenu(change_frame,#parent
                                self.feature_system_option_menu_var,#variable
                                *get_systems_list(), #options in drop-down
                                command=self.change_feature_system)
        #this is grided much later, but needs to be here
        if self.corpus.has_feature_matrix():
            self.feature_system_option_menu_var.set(self.feature_matrix.get_name())
            self.change_feature_system()

        feature_menu.grid()
        change_frame.grid(row=0,column=0,sticky=N)
        
        modify_frame = LabelFrame(option_frame,text='Modify the feature system')
        add_segment_button = Button(modify_frame, text='Add segment', command=self.add_segment)
        add_segment_button.grid()
        add_segment_button = Button(modify_frame, text='Edit segment', command=self.edit_segment)
        add_segment_button.grid()
        add_feature_button = Button(modify_frame, text='Add feature', command=self.add_feature)
        add_feature_button.grid()
        modify_frame.grid(row=0,column=1,sticky=N)
        
        coverage_frame = LabelFrame(option_frame,text='Corpus inventory coverage')
        remove_button = Button(coverage_frame, text='Remove all segments not used by the corpus', command=self.tailor_to_corpus)
        remove_button.grid()
        check_coverage_button = Button(coverage_frame, text='Check corpus inventory coverage', command=self.check_coverage)
        check_coverage_button.grid()
        coverage_frame.grid(row=0,column=2,sticky=N)
        
        button_frame = Frame(option_frame)
        ok_button = Button(button_frame, text='Save changes to this corpus\'s feature system', command=self.confirm_change_feature_system)
        ok_button.grid(sticky=W)
        cancel_button = Button(button_frame, text='Cancel', command=self.top.destroy)
        cancel_button.grid()
        button_frame.grid(row=1,column=1)
    
    def edit_segment(self):
        try:
            seg = self.feature_chart.get(self.feature_chart.curselection()[0],self.feature_chart.curselection()[0])
            seg = seg[0][0]
        except TclError:
            MessageBox.showerror(message='Please select a segment to edit.')
            return
        initial_data = (seg,self.feature_matrix[seg])
        addwindow = EditSegmentWindow(self.feature_matrix.get_feature_list(),
                                        self.feature_matrix.get_possible_values(),
                                        initial_data)
        addwindow.top.wait_window()
        if addwindow.commit:
            self.feature_matrix.add_segment(addwindow.seg,addwindow.featspec)
        self.change_feature_system()
    
    def add_segment(self):
        addwindow = EditSegmentWindow(self.feature_matrix.get_feature_list(),self.feature_matrix.get_possible_values())
        addwindow.top.wait_window()
        if addwindow.commit:
            self.feature_matrix.add_segment(addwindow.seg,addwindow.featspec)
        self.change_feature_system()
        
    def add_feature(self):
        addwindow = AddFeatureWindow(self.feature_matrix.get_feature_list())
        addwindow.top.wait_window()
        if addwindow.commit:
            self.feature_matrix.add_feature(addwindow.feature)
        self.change_feature_system()
    
    def tailor_to_corpus(self):
        corpus_inventory = self.corpus.get_inventory()
        for s in self.feature_matrix.get_segments():
            if s not in corpus_inventory:
                del self.feature_matrix[s]
        self.change_feature_system()
    
    def check_coverage(self):
        corpus_inventory = self.corpus.get_inventory()
        feature_inventory = self.feature_matrix.get_segments()
        missing = []
        for seg in corpus_inventory:
            if seg not in feature_inventory:
                missing.append(str(seg))
        if missing:
            seg_var = StringVar()
            m = Toplevel()
            m.title('Missing symbols')
            l = Label(m,text='Missing symbols:')
            l.grid(row=0,column=0)
            e = Entry(m,textvariable = seg_var)
            e.grid(row=0,column=1)
            seg_var.set(', '.join(missing))
            cancel_button = Button(m, text='Ok', command=m.destroy)
            cancel_button.grid()
            m.wait_window()
            return
        MessageBox.showinfo(message='All segments are specified for features!')
        
    
    def change_feature_system(self, event = None):
        feature_system = self.feature_system_option_menu_var.get()
        if self.feature_matrix is None or feature_system != self.feature_matrix.get_name():
            self.feature_matrix = load_binary(os.path.join(config['storage']['directory'],'FEATURE',feature_system+'.feature'))
        for child in self.feature_frame.winfo_children():
            child.destroy()
        headers = ['symbol'] + self.feature_matrix.get_feature_list()
        self.feature_chart = TableView(self.feature_frame, [(h,5) for h in headers])
        for seg in self.feature_matrix.get_segments():
            #Workaround, grr
            if seg in ['#','']: #wtf are these segments?
                continue
            self.feature_chart.append(self.feature_matrix.seg_to_feat_line(seg))


        self.feature_chart.pack(expand=True,fill='both')
        
        
    
    def confirm_change_feature_system(self):
        self.change = True
        self.top.destroy()
        
    def get_feature_matrix(self):
        return self.feature_matrix
