#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      JSMIII
#
# Created:     08/01/2014
# Copyright:   (c) JSMIII 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from tkinter import *
from tkinter.ttk import *
from tkinter import Radiobutton as OldRadiobutton
#ttk.Radiobutton doesn't support the indicatoron option, which is used for some
#of the windows
import tkinter.messagebox as MessageBox
import tkinter.filedialog as FileDialog
from corpustools.corpus.classes import (CorpusFactory, Corpus, FeatureSpecifier,
                                    Word, Segment)
import threading
import queue
import pickle
import os
import string
from configparser import ConfigParser
import collections
from codecs import open
from math import log

from corpustools.gui.basegui import (ThreadedTask, MultiListbox, PreferencesWindow,
                                    CONFIG_PATH, DEFAULT_DATA_DIR, LOG_DIR, ERROR_DIR)
try:
    from corpustools.gui.asgui import ASFunction
    as_enabled = True
except ImportError:
    as_enabled = False
from corpustools.gui.ssgui import SSFunction
from corpustools.gui.flgui import FLFunction
from corpustools.gui.pdgui import PDFunction

try:
    from PIL import Image as PIL_Image
    from PIL import ImageTk as PIL_ImageTk
    use_logo = True
except ImportError:
    use_logo = False





class GUI(Toplevel):

    def __init__(self,master,base_path):
        self.config = ConfigParser()
        self.load_config()
        
        #Set up logging
        self.log_dir = LOG_DIR
        self.errors_dir = ERROR_DIR
        
        #NON-TKINTER VARIABLES
        self.master = master
        self.show_warnings = False
        self.q = queue.Queue()
        self.corpusq = queue.Queue(1)
        self.corpus = None
        self.all_feature_systems = ['spe','hayes']
        #user defined features systems are added automatically at a later point
        self.corpus_factory = CorpusFactory()
        self.warn_about_changes = False

        #TKINTER VARIABLES ("globals")
        #main screen variabls
        self.corpus_report_label_var = StringVar()
        self.corpus_report_label_var.set('0 words loaded from corpus')
        self.corpus_button_var = StringVar()
        self.features_button_var = StringVar()
        self.search_var = StringVar()
        
        #corpus information variables
        self.feature_system_var = StringVar()
        self.feature_system_var.set('spe')
        self.feature_system_option_menu_var = StringVar()
        self.feature_system_option_menu_var.set('spe')
        self.corpus_var = StringVar()
        self.corpus_var.set('No corpus selected')
        self.corpus_size_var = IntVar()
        self.corpus_size_var.set(0)
        
        #Corpus from text variables
        self.punc_vars = [IntVar() for mark in string.punctuation]
        self.new_corpus_string_type = StringVar()
        self.new_corpus_feature_system_var = StringVar()
        self.corpus_from_text_source_file = StringVar()
        self.corpus_from_text_corpus_name_var = StringVar()
        self.corpus_from_text_output_file = StringVar()

        #MAIN SCREEN STUFF
        self.main_screen = Frame(master)
        self.main_screen.grid()
        self.info_frame = Frame(self.main_screen)
        self.info_frame.grid()

        self.check_for_feature_systems()
        corpus_info_label = Label(self.info_frame ,text='Corpus: No corpus selected')#textvariable=self.corpus_var)
        corpus_info_label.grid()
        size_info_label = Label(self.info_frame, text='Size: No corpus selected')#textvariable=self.corpus_size_var)
        size_info_label.grid()
        feature_info_label = Label(self.info_frame, textvariable=self.feature_system_var)
        feature_info_label.grid()
        self.corpus_frame = Frame(self.main_screen)
        self.corpus_frame.grid()

        #Splash image at start-up
        try:
            self.splash_image_path = os.path.join(base_path,'logo.jpg')
            self.splash_canvas = Canvas(self.corpus_frame)
            self.splash_canvas['width'] = '323'
            self.splash_canvas['height'] = '362'
            image = PIL_Image.open(self.splash_image_path)
            self.splash_image = PIL_ImageTk.PhotoImage(image,master=self.splash_canvas)
            self.splash_canvas.create_image(0,0,anchor=NW,image=self.splash_image)
            self.splash_canvas.grid()
        except:
            pass#if the image file is not found, then don't bother


    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            self.config.read(CONFIG_PATH)
        else:
            self.config['storage'] = {'directory' : DEFAULT_DATA_DIR}
            with open(CONFIG_PATH,'w') as configfile:
                self.config.write(configfile)
        self.data_dir = self.config['storage']['directory']
        
        self.trans_dir = os.path.join(self.data_dir,'TRANS')
        if not os.path.exists(self.trans_dir):
            os.makedirs(self.trans_dir)
            
        self.corpus_dir = os.path.join(self.data_dir,'CORPUS')
        if not os.path.exists(self.corpus_dir):
            os.makedirs(self.corpus_dir)
        
    def check_for_valid_corpus(function):
        def do_check(self):
            has_spelling = True
            has_transcription = True
            has_frequency = True
            missing = list()
            if self.corpus.custom:
                random_word = self.corpus.random_word()
                if not 'spelling' in random_word.descriptors:# or not random_word.spelling:
                    has_spelling = False
                    missing.append('spelling')
                if not 'transcription' in random_word.descriptors:# or not random_word.transcription:
                    has_transcription = False
                    missing.append('transcription')
                if not 'frequency' in random_word.descriptors:# or not random_word.frequency:
                    has_frequency = False
                    missing.append('token frequency')

                if self.show_warnings and not (has_spelling and has_transcription and has_frequency):
                    missing = ','.join(missing)
                    MessageBox.showwarning(message='Some information neccessary for this analysis is missing from your corpus: {}\nYou will not be able to select every option'.format(missing))
            function(self)
        return do_check

    def check_for_empty_corpus(function):
        def do_check(self):
            if self.corpus is None:
                MessageBox.showerror(message='No corpus selected')
                return
            else:
                function(self)
        return do_check

    def check_for_unsaved_changes(function):
        def do_check(self):
            if self.warn_about_changes:
                carry_on = self.issue_changes_warning()
                if not carry_on:
                    return
            function(self)

        return do_check

    def check_for_feature_systems(self):
        
        ignore = ['cmu2ipa.txt', 'cmudict.txt', 'ipa2hayes.txt', 'ipa2spe.txt']
        links = {'cmu2ipa.txt':'https://www.dropbox.com/s/dcz1hnoix2qy8d0/cmu2ipa.txt?dl=1',
                'ipa2hayes.txt':'https://www.dropbox.com/s/b5jnunz1m5pzsc6/ipa2hayes.txt?dl=1',
                'ipa2spe.txt':'https://www.dropbox.com/s/40oa9f0m2v42haq/ipa2spe.txt?dl=1'}
        for k,v in links.items():
            path = os.path.join(self.trans_dir,k)
            if not os.path.exists(path):
                from urllib.request import urlretrieve
                filename,headers = urlretrieve(v,path)
                
        for dirpath,dirname,filenames in os.walk(self.trans_dir):
            for name in filenames:
                if name in ignore:
                    continue
                system_name = name.split('.')[0]
                self.all_feature_systems.append(system_name)

    @check_for_unsaved_changes
    def quit(self,event=None):
        root.quit()

    def show_preferences(self):
        preferences = PreferencesWindow()
        preferences.wait_window()
        self.load_config()

    def update_info_frame(self):
        for child in self.info_frame.winfo_children():
            child.destroy()

        corpus_info_label = Label(self.info_frame ,text='Corpus: {}'.format(self.corpus.name))#textvariable=self.corpus_var)
        corpus_info_label.grid()

        size_info_label = Label(self.info_frame, text='Size: {}'.format(len(self.corpus)))#textvariable=self.corpus_size_var)
        size_info_label.grid()

        feature_info_label = Label(self.info_frame, text='Feature system: {}'.format(self.feature_system_var.get()) )#textvariable=self.feature_system_var)
        feature_info_label.grid()

    def navigate_to_corpus_file(self):
        custom_corpus_filename = FileDialog.askopenfilename(filetypes=(('Text files', '*.txt'),('Corpus files', '*.corpus')))
        if custom_corpus_filename:
            self.custom_corpus_path.delete(0,END)
            self.custom_corpus_path.insert(0, custom_corpus_filename)
            self.custom_corpus_name.delete(0,END)
            suggestion = os.path.basename(custom_corpus_filename).split('.')[0]
            self.custom_corpus_name.insert(0,suggestion)

    def issue_changes_warning(self):
        should_quit = MessageBox.askyesno(message=(
        'You have made changes to your corpus, but you haven\'t saved it. You will lose these changes if you load a new corpus now.\n Do you want to continue?'))
        return should_quit

    @check_for_unsaved_changes
    def choose_custom_corpus(self, event=None):

        self.custom_corpus_load_screen = Toplevel()
        self.custom_corpus_load_screen.title('Load custom corpus')
        custom_corpus_load_frame = LabelFrame(self.custom_corpus_load_screen, text='Corpus information')
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
        new_corpus_feature_frame = LabelFrame(custom_corpus_load_frame, text='Feature system to use (if transcription exists)')
        new_corpus_feature_system = OptionMenu(new_corpus_feature_frame,#parent
            self.new_corpus_feature_system_var,#variable
            'spe',#selected option,
            *[fs for fs in self.all_feature_systems])#options in drop-down
        new_corpus_feature_system.grid()
        new_corpus_feature_frame.grid(sticky=W)
        ok_button = Button(self.custom_corpus_load_screen, text='OK', command=self.confirm_custom_corpus_selection)
        cancel_button = Button(self.custom_corpus_load_screen, text='Cancel', command=self.custom_corpus_load_screen.destroy)
        ok_button.grid()
        cancel_button.grid()


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
        self.custom_corpus_load_prog_bar = Progressbar(self.custom_corpus_load_screen, mode='indeterminate')
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
        try:
            self.custom_corpus_load_screen.destroy()
        except AttributeError:
            pass #this occurs if the custom corpus was created from text, not loaded directly

        if transcription_errors is not None:
            filename = 'error_{}_{}.txt'.format(self.new_corpus_feature_system_var.get(), self.corpus.name)
            with open(os.path.join(self.errors_dir,filename), encoding='utf-8', mode='w') as f:
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
            filename,self.errors_dir)
            msg3 = 'Words with interpretable symbols will still be displayed. Consult the output file above to see how to fix this problem.'
            msg = '\n'.join([msg1, msg2, msg3])
            MessageBox.showwarning(message=msg)


        self.main_screen_refresh()

    @check_for_empty_corpus
    def search(self):

        self.search_popup = Toplevel()
        self.search_popup.title('Search {}'.format(self.corpus.name))
        search_frame = LabelFrame(self.search_popup, text='Enter search term')
        search_entry = Entry(search_frame, textvariable=self.search_var)
        search_entry.grid()
        search_frame.grid()
        ok_button = Button(self.search_popup, text='OK', command=self._search)
        cancel_button = Button(self.search_popup, text='Cancel', command=self.search_popup.destroy)
        ok_button.grid()
        cancel_button.grid()

    def _search(self):
        query = self.search_var.get()
        query = query.lower()
        try:
            self.corpus.find(query, keyerror=True)
        except KeyError:
            MessageBox.showerror(message='The word \"{}\" is not in the corpus'.format(query))
            return
        self.corpus_box.selection_clear(0,END)
        for i in range(len(self.corpus)):
            word = self.corpus_box.get(i)
            word = word[0].lower()
            try:
                word,n = word.split('(')
            except ValueError:
                pass
            if word == query:
                self.corpus_box.selection_set(i)
                self.corpus_box.see(i)
                break
        self.search_popup.destroy()


    @check_for_empty_corpus
    @check_for_valid_corpus
    def string_similarity(self):

        #Check if it's even possible to do this analysis
        
        sspopup = SSFunction(self.corpus)
        


    

    def donothing(self,event=None):
        pass


    def suggest_corpus_from_text_name(self):
        filename = FileDialog.asksaveasfilename()
        if filename:
            if not filename.endswith('.txt'):
                filename += '.txt'
            self.corpus_from_text_output_file.set(filename)

    def save_corpus_as(self):
        """
        pickles the corpus, which makes loading it WAY easier
        would be nice to have an option to save as pickle and also "export as"
        a .txt/csv file
        """
        filename = FileDialog.asksaveasfilename(filetypes=(('Corpus file', '*.corpus'),))
        if not filename:
            return

        if not filename.endswith('.corpus'):
            filename += '.corpus'
        with open(filename, 'wb') as f:
            self.corpus.feature_system = self.feature_system
            pickle.dump(self.corpus, f)
        self.warn_about_changes = False

    @check_for_unsaved_changes
    def choose_corpus(self,event=None):
        #This is always called from a menu
        self.corpus_select_screen = Toplevel()
        self.corpus_select_screen.title('Corpus select')

        corpus_frame = Frame(self.corpus_select_screen)
        corpus_area = LabelFrame(corpus_frame, text='Select a corpus')
        corpus_area.grid(sticky=W, column=0, row=0)
        subtlex_button = Radiobutton(corpus_area, text='SUBTLEX', variable=self.corpus_button_var, value='subtlex')
        subtlex_button.grid(sticky=W,row=0)
        subtlex_button.invoke()#.select() doesn't work on ttk.Button
        iphod_button = Radiobutton(corpus_area, text='IPHOD', variable=self.corpus_button_var, value='iphod')
        iphod_button.grid(sticky=W,row=1)

        features_area = LabelFrame(corpus_frame, text='Select a feature system')
        features_area.grid(sticky=E, column=1, row=0)
        spe_button = Radiobutton(features_area, text='Sound Pattern of English (Chomsky and Halle, 1968)', variable=self.features_button_var, value='spe')
        spe_button.grid(sticky=W, row=0)
        spe_button.invoke()#.select() doesn't work on ttk.Button
        hayes_button = Radiobutton(features_area, text='Hayes (2008)', variable=self.features_button_var, value='hayes')
        hayes_button.grid(sticky=W, row=1)
        corpus_frame.grid()

        button_frame = Frame(self.corpus_select_screen)
        ok_button = Button(button_frame,text='OK', command=self.confirm_corpus_selection)
        ok_button.grid(row=3, column=0)#, sticky=W, padx=3)
        cancel_button = Button(button_frame,text='Cancel', command=self.corpus_select_screen.destroy)
        cancel_button.grid(row = 3, column=1)#, sticky=W, padx=3)
        button_frame.grid()

        warning_label = Label(self.corpus_select_screen, text='Please be patient. It can take up to 30 seconds to load a corpus.')
        warning_label.grid()

    def confirm_corpus_selection(self):
        corpus_name = self.corpus_button_var.get()
        features_name = self.features_button_var.get()
        self.feature_system = features_name
        self.load_corpus(corpus_name, features_name)
        self.warn_about_changes = False

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

    def process_custom_corpus_queue(self):
        try:
            msg = self.q.get(0)
            if msg == -99:
                self.custom_corpus_load_prog_bar.stop()
                #self.corpus_load_prog_bar.destroy()
                self.custom_corpus_load_screen.destroy()
                transcription_errors = self.corpusq.get()
                corpus = self.corpusq.get()
                self.finalize_corpus(corpus, transcription_errors)
                return
            else:
                self.custom_corpus_load_prog_bar.step()
                #self.master.after(100, self.process_queue)
                self.custom_corpus_load_screen.after(3, self.process_custom_corpus_queue)
        except queue.Empty:
            #queue is empty initially for a while because it takes some time for the
            #corpus_factory.make_corpus to actually start producing worsd
            self.custom_corpus_load_screen.after(10, self.process_custom_corpus_queue)

    def load_corpus(self, corpus_name, features_name, size=10000):
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

    def main_screen_refresh(self):

        for child in self.corpus_frame.winfo_children():
            child.grid_forget()

        random_word = self.corpus.random_word()
        headers = [d for d in random_word.descriptors if not d is None or not d == '']
        self.corpus_box = MultiListbox(self.corpus_frame, [(h,10) for h in headers])
        self.update_info_frame()
        for word in self.corpus.iter_sort():
            #corpus.iter_sort is a generator that sorts the corpus dictionary
            #by keys, then yields the values in that order
            self.corpus_box.insert(END,[getattr(word,d,'???') for d in word.descriptors])
        self.corpus_box.grid()

    @check_for_empty_corpus
    def destroy_tier(self):

        word = self.corpus.random_word()
        if not word.tiers:
            MessageBox.showerror(message='No tiers have been added yet!')
            return

        self.destroy_tier_window = Toplevel()
        self.destroy_tier_window.title('Tiers')
        choose_tier = LabelFrame(self.destroy_tier_window, text='Select tier to remove')
        self.kill_tiers_list = Listbox(choose_tier)
        for tier_name in sorted(word.tiers):
            self.kill_tiers_list.insert(END,tier_name)
        self.kill_tiers_list.grid()
        kill_switch = Button(choose_tier, text='Remove', command=self.kill_tier)
        kill_all = Button(choose_tier, text='Remove all', command=self.kill_all_tiers)
        kill_switch.grid()
        kill_all.grid()
        choose_tier.grid()
        ok_button = Button(self.destroy_tier_window, text='Done', command=self.destroy_tier_window.destroy)
        ok_button.grid()

    def kill_tier(self):
        target = self.kill_tiers_list.get(self.kill_tiers_list.curselection())
        if target and self.show_warnings:
            msg = 'Are you sure you want to remove the {} tier?\nYou cannot undo this action.'.format(target)
            confirmed = MessageBox.askyesno(message=msg)
            if not confirmed:
                return

        for word in self.corpus:
            word.remove_tier(target)

        self.warn_about_changes = True
        self.destroy_tier_window.destroy()
        self.main_screen_refresh()

    def kill_all_tiers(self):
        if self.show_warnings:
            msg = 'Are you sure you want to remove all the tiers?\nYou cannot undo this action'
            confirmed = MessageBox.askyesno(message=msg)
            if not confirmed:
                return

        kill_tiers = self.kill_tiers_list.get(0,END)
        for word in self.corpus:
            for tier in kill_tiers:
                word.remove_tier(tier)

        self.warn_about_changes = True
        self.destroy_tier_window.destroy()
        self.main_screen_refresh()

    @check_for_empty_corpus
    def create_tier(self):

        word = self.corpus.random_word()
        if not 'transcription' in word.descriptors:
            MessageBox.showerror(message='No transcription column was found in your corpus. This is required for Tiers.')
            return
        self.tier_window = Toplevel()
        self.tier_window.title('Create tier')
        tier_name_frame = LabelFrame(self.tier_window, text='What do you want to call this tier?')
        self.tier_name_entry = Entry(tier_name_frame)
        self.tier_name_entry.grid()
        tier_name_frame.grid(row=0,column=0)
        tier_frame = LabelFrame(self.tier_window, text='What features define this tier?')
        self.tier_feature_list = Listbox(tier_frame)
        for feature_name in self.corpus.get_features():
            self.tier_feature_list.insert(END,feature_name)
        self.tier_feature_list.grid(row=0,column=0)
        tier_frame.grid(row=1, column=0,sticky=N)
        add_plus_feature = Button(tier_frame, text='Add [+feature]', command=self.add_plus_tier_feature)
        add_plus_feature.grid(row=1,column=0)
        add_minus_feature = Button(tier_frame, text='Add [-feature]', command=self.add_minus_tier_feature)
        add_minus_feature.grid(row=2,column=0)
        selected_frame = LabelFrame(self.tier_window, text='Selected features')
        self.selected_tier_features = Listbox(selected_frame)
        self.selected_tier_features.grid()
        selected_frame.grid(row=1,column=1,sticky=N)
        remove_feature = Button(selected_frame, text='Remove feature', command=self.remove_tier_feature)
        remove_feature.grid()
        ok_button = Button(self.tier_window, text='Create tier', command=self.add_tier_to_corpus)
        preview_button = Button(self.tier_window, text='Preview tier', command=self.preview_tier)
        cancel_button = Button(self.tier_window, text='Cancel', command=self.tier_window.destroy)
        ok_button.grid(row=2,column=0)
        preview_button.grid(row=2,column=1)
        cancel_button.grid(row=2,column=2)

    def preview_tier(self):

        features = [feature for feature in self.selected_tier_features.get(0,END)]
        matches = list()
        for seg in self.corpus.inventory:
        #for key,value in self.corpus.specifier.matrix.items():
            if all(feature in self.corpus.specifier.matrix[seg.symbol] for feature in features):
                matches.append(seg.symbol)

        if not matches:
            matches = 'No segments in this corpus have this combination of feature values'
        else:
            matches.sort()
            m = list()
            x=0
            while matches:
                m.append(matches.pop(0))
                x+=1
                if x > 10:
                    x = 0
                    m.append('\n')
            matches = ' '.join(m)

        preview_window = Toplevel()
        preview_window.title('Preview tier')
        preview_frame = LabelFrame(preview_window, text='This tier will contain these segments:')
        segs = Label(preview_frame, text=matches, justify=LEFT, anchor=W)
        segs.grid()
        preview_frame.grid()

    def add_tier_to_corpus(self):
        tier_name = self.tier_name_entry.get()
        selected_features = self.selected_tier_features.get(0,END)

        if not tier_name:
            MessageBox.showerror(message='Please enter a name for this tier')
            return
        if not selected_features:
            MessageBox.showerror(message='No features define this tier. Please select at least one feature')
            return

        for word in self.corpus:
            word.add_tier(tier_name, selected_features)

        self.warn_about_changes = True
        self.tier_window.destroy()
        self.main_screen_refresh()


    def add_plus_tier_feature(self):
        try:
            feature_name = self.tier_feature_list.get(self.tier_feature_list.curselection())
            feature_name = '+'+feature_name
            self.selected_tier_features.insert(END,feature_name)
        except TclError:
            pass

    def add_minus_tier_feature(self):
        try:
            feature_name = self.tier_feature_list.get(self.tier_feature_list.curselection())
            feature_name = '-'+feature_name
            self.selected_tier_features.insert(END,feature_name)
        except TclError:
            pass

    def remove_tier_feature(self):
        feature = self.selected_tier_features.curselection()
        if feature:
            self.selected_tier_features.delete(feature)

    def change_warnings(self):
        self.show_warnings = not self.show_warnings

    @check_for_empty_corpus
    def prod(self,shortcut=None):

        pd_popup = PDFunction(self.corpus)

    


    @check_for_unsaved_changes
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


    def navigate_to_text(self):
        text_file = FileDialog.askopenfilename(filetypes=(('Text files', '*.txt'),('Corpus files', '*.corpus')))
        if text_file:
            self.corpus_from_text_source_file.set(text_file)

    def show_feature_system(self, memory=None):

        if self.corpus is None:
            MessageBox.showwarning('No corpus selected')
            return

        if self.show_warnings:
            word = self.corpus.random_word()
            if word.tiers:
                msg = ('You have already created tiers based on a feature system.'
                        '\nChanging feature systems may give unexpected results'
                        ' and is not recommended.')
                MessageBox.showwarning(message=msg)


        if memory is None:
            #memory is set the very first time you open this option window
            #and is used in case you want to cancel
            self.feature_system_memory = self.feature_system_var.get()
            self.feature_system_option_menu_var.set(self.feature_system_var.get())
        else:
            #this is for subsequent "loops" of this function as the user
            #browses through different systems
            self.feature_system_memory = memory

        self.feature_screen = Toplevel()
        self.feature_screen.title('View/change feature system')

        if self.feature_system_option_menu_var.get() == 'spe':
            filename = 'ipa2spe.txt'
            delimiter = ','
        elif self.feature_system_option_menu_var.get() == 'hayes':
            filename = 'ipa2hayes.txt'
            delimiter = '\t'
        else:
            filename = self.feature_system_option_menu_var.get()+'.txt'
            if 'spe' in filename:
                delimiter = ','
            elif 'hayes' in filename:
                delimiter = '\t'
            else:#for some reason, this other case just won't work
                delimiter = '\t'

        with open(os.path.join(os.getcwd(), 'TRANS', filename), encoding = 'utf-8') as f:
            headers = f.readline()
            headers = headers.strip()
            headers = headers.split(delimiter)
            feature_chart = MultiListbox(self.feature_screen, [(h,5) for h in headers])
            first_line = None
            while not first_line:
                first_line = f.readline()
                first_line = first_line.strip()
            first_line = first_line.split(delimiter)
            if len(first_line) == 1:
                #this part should be fixing what happens if a guess about the
                #delimiter goes wrong in the else block up above, but it
                #doesn't seem to work
                delimiter = ',' if delimiter == '\t' else '\t'
                first_line = first_line[0].split(delimiter)
            data = [first_line[0]]
            data.extend([feature[0] for feature in first_line[1:]])
            feature_chart.insert(END, [d for d in data])
            for line in f:
                line = line.strip()
                if not line: #line is blank or just a newline
                    continue
                line = line.split(delimiter)
                symbol = line[0]
                line = [feature[0] for feature in line[1:]]
                data = [symbol]
                data.extend(line)
                feature_chart.insert(END, data)


        feature_chart.grid()
        choose_label = Label(self.feature_screen, text='Select a feature system')
        choose_label.grid()
        feature_menu = OptionMenu(self.feature_screen,#parent
                                self.feature_system_option_menu_var,#variable
                                self.feature_system_option_menu_var.get(),#selected option,
                                *[fs for fs in self.all_feature_systems], #options in drop-down
                                command=self.change_feature_system)
        #this is grided much later, but needs to be here


        feature_menu.grid()
        ok_button = Button(self.feature_screen, text='Convert corpus to new feature system', command=self.confirm_change_feature_system)
        ok_button.grid()
        cancel_button = Button(self.feature_screen, text='Go back to old feature system', command=self.cancel_change_feature_system)
        cancel_button.grid()


    def cancel_change_feature_system(self):
        self.feature_system_var.set(self.feature_system_memory)
        self.feature_screen.destroy()

    def confirm_change_feature_system(self):

        check_for_error = self.corpus.change_feature_system(self.feature_system_option_menu_var.get())
        #if there are any segments that cannot be represented in a given feature
        #system, then the corpus.change_feature_system() function returns them in a list
        #if check_for_error is an empty list, then feature changing was successful

        if check_for_error:
            #problems - print an error message
            filename = 'error_{}_{}.txt'.format(self.feature_system_option_menu_var.get(), self.corpus.name)
            with open(os.path.join(self.errors_dir,filename), encoding='utf-8', mode='w') as f:
                print('Some words in your corpus contain symbols that have no match in the \'{}\' feature system you\'ve selected.'.format(self.feature_system_option_menu_var.get()),file=f)
                print('To fix this problem, open the features file in a text editor and add the missing symbols and appropriate feature specifications\r\n', file=f)
                print('All feature files are (or should be!) located in the TRANS folder. If you have your own feature file, just drop it into that folder before loading CorpusTools.\r\n\r\n', file=f)
                print('The following segments could not be represented:', file=f)
                for key in sorted(list(check_for_error.keys())):
                    words = sorted(check_for_error[key])
                    words = ','.join(words)
                    sep = '\r\n\n'
                    print('Symbol: {}\r\nWords: {}\r\n{}'.format(key,words,sep), file=f)
            msg1 = 'Not every symbol in your corpus can be interpreted with this feature system.'
            msg2 = 'A file called {} has been placed in your ERRORS folder ({}) explaining this problem in more detail.'.format(filename,self.errors_dir)
            msg3 = 'No changes have been made to your corpus'
            msg = '\n'.join([msg1, msg2, msg3])
            MessageBox.showwarning(message=msg)
            self.feature_screen.destroy()

        else:
            #no problems - update feature system and change some on-screen info
            self.warn_about_changes = True
            self.feature_system_var.set(self.feature_system_option_menu_var.get())
            self.feature_system_memory = self.feature_system_var.get()
            self.update_info_frame()
            self.feature_screen.destroy()

    def change_feature_system(self, event=None):
        word = self.corpus.random_word()
        if not hasattr(word, 'transcription'):
            MessageBox.showerror(message=('No transcription column was found in your corpus.'
            '\nTranscription is necessary to use feature systems'))
            return

        self.feature_screen.destroy()
        self.show_feature_system(memory=self.feature_system_memory)


    def acoustic_sim(self):

        if not as_enabled:
            MessageBox.showerror(message=('Missing dependencies for either \'numpy\', \'scipy\' or both.'
            '\nAcoustic similarity cannot be run without both of them installed.'))
            return
        self.as_popup = ASFunction()
        

    @check_for_empty_corpus
    def functional_load(self):

        fl_popup = FLFunction(self.corpus)
        


    def export_to_text_file(self):
        filename = FileDialog.asksaveasfilename()
        if not filename:
            return

        word = self.corpus.random_word()
        values = sorted(word.descriptors)
        with open(filename, encoding='utf-8', mode='w') as f:
            print(','.join(sorted(word.descriptors)), file=f)
            for key in self.corpus.iter_sort():
                #word = self.corpus[key]
                for value in values:
                    print(','.join(str(getattr(word, value)) for value in values), file=f)
        self.warn_about_changes = False


    





def make_menus(root,app):

    menubar = Menu(root)
    corpusmenu = Menu(menubar, tearoff=0)
    corpusmenu.add_command(label='Choose built-in corpus...', command=app.choose_corpus)
    corpusmenu.add_command(label='Use custom corpus...', command=app.choose_custom_corpus)
    corpusmenu.add_command(label='Create corpus from text...', command=app.corpus_from_text)
    savemenu = Menu(corpusmenu, tearoff=0)
    savemenu.add_command(label='Save as corpus file (faster loading in CorpusTools)...', command=app.save_corpus_as)
    savemenu.add_command(label='Save as text file (use with spreadsheets etc.)...', command=app.export_to_text_file)
    corpusmenu.add_cascade(label='Save', menu=savemenu)
    corpusmenu.add_command(label="Quit", command=app.quit, accelerator='Ctrl+Q')
    menubar.add_cascade(label="Corpus", menu=corpusmenu)

    optionmenu = Menu(menubar, tearoff=0)
    #optionmenu.add_command(label='Search corpus...', command=app.search)
    optionmenu.add_command(label='Preferences...', command=app.show_preferences)
    optionmenu.add_command(label='View/change feature system...', command=app.show_feature_system)
    optionmenu.add_command(label='Add Tier...', command=app.create_tier)
    optionmenu.add_command(label='Remove Tier...', command=app.destroy_tier)
    optionmenu.add_checkbutton(label='Show warnings', onvalue=True, offvalue=False, variable=app.show_warnings, command=app.change_warnings)
    menubar.add_cascade(label='Options', menu=optionmenu)
    optionmenu.invoke(4)#start with the checkmark for the 'show warning' option turned on

    calcmenu = Menu(menubar, tearoff=0)
    calcmenu.add_command(label='Calculate string similarity...', command=app.string_similarity)
    calcmenu.add_command(label='Calculate predictability of distribution...', command=app.prod)
    calcmenu.add_command(labe='Calculate functional load...', command=app.functional_load)
    calcmenu.add_command(labe='Calculate acoustic similarity...', command=app.acoustic_sim)
    menubar.add_cascade(label='Analysis', menu=calcmenu)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help...", command=app.donothing)
    helpmenu.add_command(label="About...", command=app.donothing)
    menubar.add_cascade(label="Help", menu=helpmenu)
    root.config(menu=menubar)

