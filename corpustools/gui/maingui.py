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
#import string_similarity
import corpustools.symbolsim.string_similarity as morph_relatedness
import corpustools.funcload.functional_load as FL
import collections
from codecs import open
from math import log

from corpustools.gui.basegui import (ThreadedTask, MultiListbox, PreferencesWindow,
                                    CONFIG_PATH, DEFAULT_DATA_DIR, LOG_DIR)
from corpustools.gui.asgui import ASFunction

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
        self.errors_dir = os.path.join(self.log_dir,'ERRORS')
        if not os.path.exists(self.errors_dir):
            os.makedirs(self.errors_dir)
        
        #NON-TKINTER VARIABLES
        self.master = master
        self.show_warnings = False
        self.q = queue.Queue()
        self.corpusq = queue.Queue(1)
        self.corpus = None
        self.all_feature_systems = ['spe','hayes']
        #user defined features systems are added automatically at a later point
        self.corpus_factory = CorpusFactory()
        self.tooltip_delay = 1500
        self.warn_about_changes = False

        #TKINTER VARIABLES ("globals")
        #main screen variabls
        self.corpus_report_label_var = StringVar()
        self.corpus_report_label_var.set('0 words loaded from corpus')
        self.corpus_button_var = StringVar()
        self.features_button_var = StringVar()
        self.search_var = StringVar()
        #string similarity variables
        self.string_similarity_query_var = StringVar()
        self.string_similarity_filename_var = StringVar()
        self.string_similarity_typetoken_var = StringVar()
        self.string_similarity_stringtype_var = StringVar()
        self.string_similarity_pairs_var = StringVar()
        self.string_similarity_comparison_type_var = StringVar()
        self.string_similarity_one_pair1_var = StringVar()
        self.string_similarity_one_pair2_var = StringVar()
        self.string_similarity_min_rel_var = StringVar()
        self.string_similarity_max_rel_var = StringVar()
        self.string_similarity_relator_type_var = StringVar()
        #corpus information variables
        self.feature_system_var = StringVar()
        self.feature_system_var.set('spe')
        self.feature_system_option_menu_var = StringVar()
        self.feature_system_option_menu_var.set('spe')
        self.corpus_var = StringVar()
        self.corpus_var.set('No corpus selected')
        self.corpus_size_var = IntVar()
        self.corpus_size_var.set(0)
        #entropy calculation variables
        self.entropy_tier_var = StringVar()
        self.entropy_typetoken_var = StringVar()
        self.letter1_var = StringVar()
        self.letter2_var = StringVar()
        self.seg1_var = StringVar()
        self.seg2_var = StringVar()
        self.lhs_feature_var = StringVar()
        self.rhs_feature_var = StringVar()
        self.lhs_seg_var = StringVar()
        self.rhs_seg_var = StringVar()
        self.entropy_filename_var = StringVar()
        self.entropy_exhaustive_var = IntVar()
        self.entropy_uniqueness_var = IntVar()
        self.entropy_exclusive_var = IntVar()
        self.entropy_result_list = None
        self.calculating_entropy_screen = None
        #Corpus from text variables
        self.punc_vars = [IntVar() for mark in string.punctuation]
        self.new_corpus_string_type = StringVar()
        self.new_corpus_feature_system_var = StringVar()
        self.corpus_from_text_source_file = StringVar()
        self.corpus_from_text_corpus_name_var = StringVar()
        self.corpus_from_text_output_file = StringVar()
        #Functional load variables
        self.fl_frequency_cutoff_var = StringVar()
        self.fl_homophones_var = StringVar()
        self.fl_relative_count_var = StringVar()
        self.fl_seg1_var = StringVar()
        self.fl_seg2_var = StringVar()
        self.fl_q = queue.Queue()
        self.fl_results_table = None
        self.fl_type_var = StringVar()

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
    def string_similarity(self):

        #Check if it's even possible to do this analysis
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

        self.string_similarity_popup = Toplevel()
        self.string_similarity_popup.title('String similarity')
        try:
            selection = self.corpus_box.get(self.corpus_box.curselection())[0][0]
        except TclError:
            #this means that nothing was selected in the multibox
            selection = ''

        relator_type_frame = LabelFrame(self.string_similarity_popup, text='String similarity algorithm')
        self.relator_selection = Listbox(relator_type_frame)
        for rtype in ['Khorsi', 'Edit distance', 'Phonological edit distance']:
            self.relator_selection.insert(0, rtype)
        self.relator_selection.grid()
        relator_type_frame.grid(row=0,column=0,sticky=N)

        comparison_type_frame = LabelFrame(self.string_similarity_popup, text='Comparison type')
        word1_frame = Frame(comparison_type_frame)
        one_word_radiobutton = Radiobutton(word1_frame, text='Compare one word to entire corpus',
                                    variable=self.string_similarity_comparison_type_var, value='one')
        one_word_radiobutton.grid(sticky=W)
        one_word_radiobutton.invoke()
        word1_frame.grid(sticky=W)
        word1_entry = Entry(word1_frame, textvariable=self.string_similarity_query_var)
        word1_entry.delete(0,END)
        word1_entry.insert(0,selection)
        word1_entry.grid(sticky=W)

        one_pair_frame = Frame(comparison_type_frame)
        one_pair_radiobutton = Radiobutton(one_pair_frame, text='Compare a single pair of words to each other',
                                    variable=self.string_similarity_comparison_type_var, value='one_pair')
        one_pair_radiobutton.grid(row=0, column=0, sticky=W)
        two_words_frame = Frame(one_pair_frame)
        first_word_label = Label(two_words_frame, text='Word 1: ')
        first_word_label.grid(row=1, column=0, sticky=W)
        first_word_entry = Entry(two_words_frame, textvariable=self.string_similarity_one_pair1_var)
        first_word_entry.grid(row=1, column=1, sticky=W)
        second_word_label = Label(two_words_frame, text='Word 2: ')
        second_word_label.grid(row=2, column=0, sticky=W)
        second_word_entry = Entry(two_words_frame, textvariable=self.string_similarity_one_pair2_var)
        second_word_entry.grid(row=2, column=1, sticky=W)
        two_words_frame.grid(sticky=W)
        one_pair_frame.grid(sticky=W)

        word_pairs_frame = Frame(comparison_type_frame)

        pairs_radiobutton = Radiobutton(word_pairs_frame, text='Compare a list of pairs of words',
                                        variable=self.string_similarity_comparison_type_var, value='pairs')
        pairs_radiobutton.grid(sticky=W)
        get_word_pairs_button = Button(word_pairs_frame, text='Choose word pairs file', command=self.get_word_pairs_file)
        get_word_pairs_button.grid(sticky=W)
        get_word_pairs_label = Label(word_pairs_frame, textvariable=self.string_similarity_pairs_var)
        get_word_pairs_label.grid(sticky=W)
        word_pairs_frame.grid(sticky=W)


        comparison_type_frame.grid(row=0,column=1,sticky=N)

        options_frame = LabelFrame(self.string_similarity_popup, text='Options')
        typetoken_frame = LabelFrame(options_frame, text='Type or Token')
        type_button = Radiobutton(typetoken_frame, text='Count types', variable=self.string_similarity_typetoken_var, value='type')
        type_button.grid(sticky=W)
        type_button.invoke()
        token_button = Radiobutton(typetoken_frame, text='Count tokens', variable=self.string_similarity_typetoken_var, value='token')
        token_button.grid(sticky=W)
        if not has_frequency:
            token_button.configure(state=('disabled'))
        typetoken_frame.grid(column=0, row=0, sticky=W)
        stringtype_frame = LabelFrame(options_frame, text='String type')
        spelling_button = Radiobutton(stringtype_frame, text='Compare spelling', variable=self.string_similarity_stringtype_var, value='spelling')
        spelling_button.grid(sticky=W)
        spelling_button.invoke()
        if not has_spelling:
            transcription_button.configure(state=('disabled'))
        transcription_button = Radiobutton(stringtype_frame, text='Compare transcription', variable=self.string_similarity_stringtype_var, value='transcription')
        transcription_button.grid(sticky=W)
        if not has_transcription:
            transcription_button.configure(state=('disabled'))
        stringtype_frame.grid(column=0, row=1, sticky=W)
        threshold_frame = LabelFrame(options_frame, text='Return only results with similarity between...')
        min_label = Label(threshold_frame, text='Minimum: ')
        min_label.grid(row=0, column=0)
        min_rel_entry = Entry(threshold_frame, textvariable=self.string_similarity_min_rel_var)
        min_rel_entry.grid(row=0, column=1, sticky=W)
        max_label = Label(threshold_frame, text='Maximum: ')
        max_label.grid(row=1, column=0)
        max_rel_entry = Entry(threshold_frame, textvariable=self.string_similarity_max_rel_var)
        max_rel_entry.grid(row=1, column=1, sticky=W)
        threshold_frame.grid(column=0, row=2, sticky=W)
        options_frame.grid(row=0, column=2, sticky=N)

        button_frame = Frame(self.string_similarity_popup)
        ok_button = Button(button_frame, text='OK', command=self.calculate_string_similarity)
        ok_button.grid(row=0,column=0)
        if not has_spelling and has_transcription:
            ok_button.state = DISABLED
        cancel_button = Button(button_frame, text='Cancel', command=self.cancel_string_similarity)
        cancel_button.grid(row=0, column=1)
        info_button = Button(button_frame, text='About this function...', command=self.string_similarity_info)
        info_button.grid(row=0,column=2)
        button_frame.grid(row=1)

    def get_word_pairs_file(self):
        filename = FileDialog.askopenfilename()
        if filename:
            self.string_similarity_pairs_var.set(filename)
        if not filename.endswith('.txt'):
            filename += '.txt'

    def print_string_similarity_results(self, results):

        if self.string_similarity_comparison_type_var.get() == 'one':
            suggestion = self.string_similarity_query_var.get()
            if suggestion:
                suggestion = 'string_similarity_{}.txt'.format(suggestion)
            else:
                suggestion = ''

        elif self.string_similarity_comparison_type_var.get() == 'pairs':
            suggestion = self.string_similarity_pairs_var.get()
            if suggestion:
                suggestion = os.path.split(suggestion)[-1]
                suggestion = os.path.splitext(suggestion)[0]
                suggestion = 'string_similarity_pairs_{}.txt'.format(suggestion)
            else:
                suggestion = ''

        elif self.string_similarity_comparison_type_var.get() == 'one_pair':
            word1 = self.string_similarity_one_pair1_var.get()
            word2 = self.string_similarity_one_pair2_var.get()
            if (word1 and word2):
                suggestion = 'string_similarity_{}_{}.txt'.format(word1, word2)
            else:
                suggestion = ''

        filename = FileDialog.asksaveasfilename(initialfile=suggestion)
        if not filename:
            return

        self.string_similarity_filename_var.set(filename)

        if self.string_similarity_comparison_type_var.get() == 'one':
            threshold = self.string_similarity_threshold_var.get()
            if threshold:
                threshold = int(threshold)
            else:
                threshold = None
            morph_relatedness.print_one_word_results(filename,
                                                self.string_similarity_query_var.get(),
                                                results, threshold)
        else:
            morph_relatedness.print_pairs_results(filename, results)

    def string_similarity_info(self):

        info_popup = Toplevel()
        info_popup.title('About the string similarity function')
        description_frame = LabelFrame(info_popup, text='Brief description')
        text = ('This function calculates the similarity between words in the corpus,'
                ' based on either their spelling or their transcription. Similarity '
                'is a function of the longest common shared sequences of graphemes '
                'or phonemes (weighted by their frequency of occurrence in the corpus), '
                'subtracting out the non-shared graphemes or phonemes. The spelling '
                'version was originally proposed as a measure of morphological relatedness,'
                ' but is more accurately described as simply a measure of string similarity.')
        description_label = Label(description_frame, text=text)
        description_label.config(wraplength=600)
        description_label.grid()
        description_frame.grid(sticky=W)
        citation_frame = LabelFrame(info_popup, text='Original source')
        citation_label = Label(citation_frame, text='Khorsi, A. 2012. On Morphological Relatedness. Natural Language Engineering, 1-19.')
        citation_label.grid()
        citation_frame.grid(sticky=W)
        author_frame = LabelFrame(info_popup, text='Coded by')
        author_label = Label(author_frame, text='Micheal Fry')
        author_label.grid()
        author_frame.grid(sticky=W)

    def about_entropy(self):

        info_popup = Toplevel()
        info_popup.title('About the predictability of distribution function')
        description_frame = LabelFrame(info_popup, text='Brief description')
        description_label = Label(description_frame, text=('This function calculates'
        ' the predictability of distribution of two sounds, using the measure of entropy'
        ' (uncertainty). Sounds that are entirely predictably distributed (i.e., in'
        ' complementary distribution, commonly assumed to be allophonic), will have'
        ' an entropy of 0. Sounds that are perfectly overlapping in their distributions'
        ' will have an entropy of 1.'))
        description_label.config(wraplength=600)
        description_label.grid()
        description_frame.grid(sticky=W)
        citation_frame = LabelFrame(info_popup, text='Original source')
        citation_label = Label(citation_frame, text='Hall, K.C. 2009. A probabilistic model of phonological relationships from contrast to allophony. PhD dissertation, The Ohio State University.')
        citation_label.grid()
        citation_frame.grid(sticky=W)
        author_frame = LabelFrame(info_popup, text='Coded by')
        author_label = Label(author_frame, text='Scott Mackie, Blake Allen')
        author_label.grid()
        author_frame.grid(sticky=W)

    def calculate_string_similarity(self):

        #First check if the word is in the corpus

        if not self.relator_selection.curselection():
            MessageBox.showerror(message='Please select a string similarity algorithm')
            return
        else:
            relator_type = self.relator_selection.get(self.relator_selection.curselection())
            if relator_type == 'Khorsi':
                relator_type = 'khorsi'
            elif relator_type == 'Edit distance':
                relator_type = 'edit_distance'
            elif relator_type == 'Phonological edit distance':
                relator_type = 'phono_edit_distance'

        comp_type = self.string_similarity_comparison_type_var.get()
        if comp_type == 'one':
            query = self.string_similarity_query_var.get()
            if not query:
                MessageBox.showerror(message='Please enter a word')
            try:
                self.corpus.find(query,keyerror=True)
            except KeyError:
                message = 'The word \"{}\" is not in the corpus'.format(query)
                MessageBox.showerror(message=message)
                return
        elif comp_type == 'pairs':
            if not self.string_similarity_pairs_var.get():
                MessageBox.showerror(message='Please select a file of word pairs')
                return

        elif comp_type == 'one_pair':
            #check if results are already open
            query1 = self.string_similarity_one_pair1_var.get()
            query2 = self.string_similarity_one_pair2_var.get()
            if not (query1 and query2):
                MessageBox.showerror(message=('You selected to compare a pair,'
                            'but only entered one word.\Please enter another word'))
                return
            try:
                self.corpus.find(query1,keyerror=True)
            except KeyError:
                message = 'The word \"{}\" is not in the corpus'.format(query)
                MessageBox.showerror(message=message)
                return

            try:
                self.corpus.find(query2,keyerror=True)
            except KeyError:
                message = 'The word \"{}\" is not in the corpus'.format(query)
                MessageBox.showerror(message=message)
                return

        #If it's all good, then calculate relatedness
        string_type = self.string_similarity_stringtype_var.get()
        typetoken = self.string_similarity_typetoken_var.get()
        output_filename = self.string_similarity_filename_var.get()
        min_rel = self.string_similarity_min_rel_var.get()
        max_rel = self.string_similarity_max_rel_var.get()
        if min_rel:
            min_rel = float(min_rel)
        else:
            min_rel = None

        if max_rel:
            max_rel = float(max_rel)
        else:
            max_rel = None



        if self.string_similarity_comparison_type_var.get() == 'one':
            query = self.string_similarity_query_var.get()
            results = morph_relatedness.string_similarity_word('',relator_type,
                                                string_type, typetoken, query,
                                                min_rel, max_rel, self.corpus, output_filename='return_data')
            string_similarity_results_popup = Toplevel()
            title = 'Counting {}, Comparing {}'.format(self.string_similarity_typetoken_var.get(),
                                                     self.string_similarity_stringtype_var.get())
            string_similarity_results_popup.title(title)
            string_similarity_results_frame = Frame(string_similarity_results_popup)
            string_similarity_results_box = MultiListbox(string_similarity_results_popup,
                        [('Relatedness to \"{}\"'.format(self.string_similarity_query_var.get()),25),
                        (string_type, 15),
                        ('Type or token', 10),
                        ('Algorithm type', 10)
                        ])

            for result in results:
                word, similarity = result
                string_similarity_results_box.insert(END,[word, similarity, typetoken, relator_type])

        elif self.string_similarity_comparison_type_var.get() == 'pairs':
            query = self.string_similarity_pairs_var.get()
            results = morph_relatedness.string_similarity_pairs('', relator_type,
                                                    string_type, typetoken, query,
                                                    'return_data', min_rel, max_rel, self.corpus)
            string_similarity_results_popup = Toplevel()
            title = 'Comparing pairs of words'.format(self.string_similarity_typetoken_var.get(),
                                                     self.string_similarity_stringtype_var.get())
            string_similarity_results_popup.title(title)
            string_similarity_results_frame = Frame(string_similarity_results_popup)
            string_similarity_results_box = MultiListbox(string_similarity_results_popup,
                        [('Word 1',20),
                        ('Word 2', 20),
                        ('Similarity', 10),
                        ('Type or token', 10),
                        ('Algorithm type', 10)])

            for result in results:
                w1, w2, similarity = result
                string_similarity_results_box.insert(END,[w1, w2, similarity, typetoken, relator_type])

        elif self.string_similarity_comparison_type_var.get() == 'one_pair':
            word1 = self.string_similarity_one_pair1_var.get()
            word2 = self.string_similarity_one_pair2_var.get()
            results = morph_relatedness.string_similarity_single_pair('', relator_type, string_type, word1, word2, self.corpus)
            results = list(results)
            results.append(typetoken)
            results.append(relator_type)
            string_similarity_results_popup = Toplevel()
            string_similarity_results_popup.title('String similarity results')
            string_similarity_results_frame = Frame(string_similarity_results_popup)
            string_similarity_results_box = MultiListbox(string_similarity_results_popup,
                        [('Word 1',20),
                        ('Word 2', 20),
                        ('Similarity', 20),
                        ('Type or token', 10),
                        ('Algorithm type', 10)])
            string_similarity_results_box.insert(END,results)

        #display results on screen
        string_similarity_results_box.grid()
        string_similarity_results_frame.grid()
        print_frame = Frame(string_similarity_results_frame)
        print_button = Button(print_frame, text='Save results to file', command=lambda x=results: self.print_string_similarity_results(x))
        print_button.grid()
        print_frame.grid()

    def cancel_string_similarity(self):
        self.string_similarity_popup.destroy()

    def donothing(self,event=None):
        pass

    def suggest_entropy_filename(self):
        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()
        suggested_name = 'entropy_of_{}_{}_{}.txt'.format(seg1, seg2, self.entropy_typetoken_var.get())
        filename = FileDialog.asksaveasfilename(initialdir=os.getcwd(),
                                                initialfile=suggested_name,
                                                defaultextension='.txt')
        return filename

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
    def entropy(self,shortcut=None):

        #check if it's possible to do this analysis
        has_transcription = True
        has_frequency = True
        missing = list()
        if self.corpus.custom:
            random_word = self.corpus.random_word()
            if not 'transcription' in random_word.descriptors:
                has_transcription = False
                missing.append('transcription')
            if not 'frequency' in random_word.descriptors:
                has_frequency = False
                missing.append('token frequency')

            if self.show_warnings and not has_transcription:
                MessageBox.showwarning(message='Your corpus lacks a transcription column, which is necessary for this analysis')
                return

            elif self.show_warnings and not has_frequency:
                missing = ','.join(missing)
                MessageBox.showwarning(message='Your corpus lacks a token frequency count. This option will be disabled.')


        self.entropy_main_screen = Toplevel()
        self.entropy_main_screen.title('Predictability of distribution calculation')

        ipa_frame = LabelFrame(self.entropy_main_screen, text='Sounds')

        ipa_frame_tooltip = ToolTip(ipa_frame,
                                    delay=self.tooltip_delay,follow_mouse=True,
                                    text=('Choose the two sounds whose '
        'predictability of distribution you want to calculate. The order of the '
        'two sounds is irrelevant. The symbols you see here should automatically'
        ' match the symbols used anywhere in your corpus.'))
        segs = [seg.symbol for seg in self.corpus.inventory]
        segs.sort()
        seg1_frame = LabelFrame(ipa_frame, text='Choose first symbol')
        colmax = 10
        col = 0
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(seg1_frame, text=seg, variable=self.seg1_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        seg1_frame.grid()

        seg2_frame = LabelFrame(ipa_frame, text='Choose second symbol')
        colmax = 10
        col = 0
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(seg2_frame, text=seg, variable=self.seg2_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        seg2_frame.grid()


        option_frame = LabelFrame(self.entropy_main_screen, text='Options')

        tier_frame = LabelFrame(option_frame, text='Tier')
        tier_frame_tooltip = ToolTip(tier_frame,
                                    delay=self.tooltip_delay, follow_mouse=True,
                                    text=('Choose which tier predictability should'
                                    'be calculated over (e.g., the whole transcription'
                                    ' vs. a tier containing only [+voc] segments).'
                                    'New tiers can be created from the Corpus menu.'))
        tier_options = ['transcription']
        word = self.corpus.random_word()
        tier_options.extend([tier for tier in word.tiers])
        tier_options_menu = OptionMenu(tier_frame,self.entropy_tier_var,'transcription',*tier_options)
        tier_options_menu.grid()
        tier_frame.grid(row=0,column=0)

        typetoken_frame = LabelFrame(option_frame, text='Type or Token')
        typetoken_tooltip = ToolTip(typetoken_frame,
                                    delay=self.tooltip_delay, follow_mouse=True,
                                    text=('Choose what kind of frequency should '
                                    'be used for the calculations. Type frequency'
                                    ' means each word is counted once. Token frequency'
                                    ' means each word is counted as often as it occurs'
                                    ' in the corpus.'))
        type_button = Radiobutton(typetoken_frame, text='Count types', variable=self.entropy_typetoken_var, value='type')
        type_button.grid(sticky=W)
        type_button.invoke()
        token_button = Radiobutton(typetoken_frame, text='Count tokens', variable=self.entropy_typetoken_var, value='token')
        token_button.grid(sticky=W)
        if not has_frequency:
            token_button.configure(state=('disabled'))
        typetoken_frame.grid(row=1, column=0)

        ex_frame = LabelFrame(option_frame, text='Exhaustivity and uniqueness')
        ex_frame_tooltip = ToolTip(ex_frame,
                                    delay=self.tooltip_delay, follow_mouse=True,
                                    text=('Indicate whether you want the program'
                                    ' to check for exhausitivity and/or uniqueness.'
                                    ' Checking for exhaustivity means the program '
                                    'will make sure that you have selected environments'
                                    ' that cover all instances of the two sounds in the'
                                    ' corpus. Checking for uniqueness means the program'
                                    ' will check to make sure that the environments you'
                                    ' have selected don\'t overlap with one another. It'
                                    ' is recommended that both options are used unless '
                                    'there is a specific reason to do otherwise.'))
        check_exhaustive = Checkbutton(ex_frame, text='Check for exhaustivity', variable=self.entropy_exhaustive_var)
        self.entropy_exhaustive_var.set(1)
        check_exhaustive.grid()
        check_uniqueness = Checkbutton(ex_frame, text='Check for uniqueness', variable=self.entropy_uniqueness_var)
        check_uniqueness.grid()
        self.entropy_uniqueness_var.set(1)
        ex_frame.grid(row=2, column=0)

##        output_file_frame = LabelFrame(option_frame, text='Output file path')
##        self.entropy_output_file_label = Label(output_file_frame, textvariable=self.entropy_filename_var)
##        self.entropy_output_file_label.grid()
##        suggest_filename_button = Button(output_file_frame,
##                                        text='Choose file name and location',
##                                        command=self.suggest_entropy_filename)
##        suggest_filename_button.grid()
##        output_file_frame.grid(row=3, column=0)

        button_frame = Frame(self.entropy_main_screen)
        ok_button = Button(button_frame, text='Next step...', command=self.entropy_options)
        ok_button.grid(row=0, column=0)
        cancel_button = Button(button_frame, text='Cancel', command=self.cancel_entropy)
        cancel_button.grid(row=0, column=1)
        info_button = Button(button_frame, text='About this function...', command=self.about_entropy)
        info_button.grid(row=0, column=2)

        ipa_frame.grid(row=0, column=0, sticky=N)
        option_frame.grid(row=0, column=1, sticky=N)
        button_frame.grid(row=1,column=0)

    def add_plus_feature_lhs(self):
        try:
            feature_name = self.lhs_feature_list.get(self.lhs_feature_list.curselection())
            feature_name = '+'+feature_name
            self.lhs_selected_list.insert(END,feature_name)
        except TclError:
            pass

    def add_minus_feature_lhs(self):
        try:
            feature_name = self.lhs_feature_list.get(self.lhs_feature_list.curselection())
            feature_name = '-'+feature_name
            self.lhs_selected_list.insert(END,feature_name)
        except TclError:
            pass

    def add_plus_feature_rhs(self):
        try:
            feature_name = self.rhs_feature_list.get(self.rhs_feature_list.curselection())
            feature_name = '+'+feature_name
            self.rhs_selected_list.insert(END,feature_name)
        except TclError:
            pass


    def add_minus_feature_rhs(self):
        try:
            feature_name = self.rhs_feature_list.get(self.rhs_feature_list.curselection())
            feature_name = '-'+feature_name
            self.rhs_selected_list.insert(END,feature_name)
        except TclError:
            pass


    def cancel_entropy(self):
        self.seg1_var = StringVar()
        self.seg2_var = StringVar()
        self.entropy_filename_var = StringVar()
        self.destroy_entropy_results_table()
        self.entropy_main_screen.destroy()

    def entropy_options(self):

        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()
        fname = self.entropy_filename_var.get()

        if not (seg1 and seg2):
            MessageBox.showerror(message='Please ensure you have selected 2 segments and chosen a output file name')
            return

        self.entropy_main_screen.withdraw()
        self.entropy_screen = Toplevel()
        self.entropy_screen.title('Environments for calculating predictability of distribution')


        env_frame = LabelFrame(self.entropy_screen, text='Construct environment')
        env_frame_tooltip = ToolTip(env_frame,
                                    delay=self.tooltip_delay, follow_mouse=False,
                                    text=('This screen allows you to construct multiple'
                                    ' environments in which to calculate predictability'
                                    ' of distribution. For each environment, you can specify'
                                    ' either the left-hand side or the right-hand side, or '
                                    'both. Each of these can be specified using either features or segments.'))

        lhs_frame = LabelFrame(env_frame, text='Left hand side')

        lhs_feature_frame = LabelFrame(lhs_frame, text='Feature-based environment')
        lhs_feature_entry_explanation = Label(lhs_feature_frame, text='Select one or more features to match')
        lhs_feature_entry_explanation.grid(row=0)
        self.lhs_feature_list = Listbox(lhs_feature_frame)
        for feature_name in self.corpus.get_features():
            self.lhs_feature_list.insert(END,feature_name)
        self.lhs_feature_list.grid(row=1, column=0)
        self.lhs_selected_list = Listbox(lhs_feature_frame)
        lhs_button_frame = Frame(lhs_feature_frame)
        add_plus = Button(lhs_button_frame, text='Add [+feature]', command=self.add_plus_feature_lhs)
        add_plus.grid(row=0,column=0)
        add_minus = Button(lhs_button_frame, text='Add [-feature]', command=self.add_minus_feature_lhs)
        add_minus.grid(row=1, column=0)
        clear_features = Button(lhs_button_frame, text='Clear list', command=lambda x=0:self.lhs_selected_list.delete(x,END))
        clear_features.grid(row=2, column=0)
        lhs_button_frame.grid(row=1,column=1)
        self.lhs_selected_list.grid(row=1, column=2)

        lhs_seg_frame = LabelFrame(lhs_frame, text='Segment-based environment')
        lhs_seg_entry_explanation = Label(lhs_seg_frame, text='Select a segment to match')
        lhs_seg_entry_explanation.grid()
        segs = [seg.symbol for seg in self.corpus.inventory]
        segs.sort()
        segs_frame = Frame(lhs_seg_frame)
        col = 0
        colmax = 8
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(segs_frame, text=seg, variable=self.lhs_seg_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        segs_frame.grid()
        self.lhs_seg_entry = Entry(lhs_seg_frame,textvariable=self.lhs_seg_var)
        self.lhs_seg_entry.grid()

        lhs_feature_frame.grid(row=0, column=0, sticky=N)
        lhs_seg_frame.grid(row=0, column=1, sticky=N)
        lhs_frame.grid(row=0, column=0, padx=3)


        #RIGHT HAND SIDE STARTS HERE
        rhs_frame = LabelFrame(env_frame, text='Right hand side')

        rhs_feature_frame = LabelFrame(rhs_frame, text='Feature-based environment')
        rhs_feature_entry_explanation = Label(rhs_feature_frame, text='Select one or more features to match')
        rhs_feature_entry_explanation.grid(row=0)
        self.rhs_feature_list = Listbox(rhs_feature_frame)
        for feature_name in self.corpus.get_features():
            self.rhs_feature_list.insert(END,feature_name)
        self.rhs_feature_list.grid(row=1, column=0)
        self.rhs_selected_list = Listbox(rhs_feature_frame)
        rhs_button_frame = Frame(rhs_feature_frame)
        add_plus = Button(rhs_button_frame, text='Add [+feature]', command=self.add_plus_feature_rhs)
        add_plus.grid(row=0,column=0)
        add_minus = Button(rhs_button_frame, text='Add [-feature]', command=self.add_minus_feature_rhs)
        add_minus.grid(row=1, column=0)
        clear_features = Button(rhs_button_frame, text='Clear list', command=lambda x=0:self.rhs_selected_list.delete(x,END))
        clear_features.grid(row=2, column=0)
        rhs_button_frame.grid(row=1,column=1)
        self.rhs_selected_list.grid(row=1, column=2)

        rhs_seg_frame = LabelFrame(rhs_frame, text='Segment-based environment')
        rhs_seg_entry_explanation = Label(rhs_seg_frame, text='Select a segment to match')
        rhs_seg_entry_explanation.grid()
        segs = [seg.symbol for seg in self.corpus.inventory]
        segs.sort()
        segs_frame = Frame(rhs_seg_frame)
        col = 0
        colmax = 8
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(segs_frame, text=seg, variable=self.rhs_seg_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        segs_frame.grid()
        self.rhs_seg_entry = Entry(rhs_seg_frame,textvariable=self.rhs_seg_var)
        self.rhs_seg_entry.grid()

        rhs_feature_frame.grid(row=0, column=0, sticky=N)
        rhs_seg_frame.grid(row=0, column=1, sticky=N)
        rhs_frame.grid(row=1, column=0, padx=3)
        env_frame.grid(row=0, column=0)


        #BUTTON FRAME STARTS HERE
        button_frame = Frame(self.entropy_screen)

        left_frame = Frame(button_frame)
        add_env_to_list = Button(left_frame, text='Add this environment to list', command=self.confirm_entropy_options)
        add_env_to_list.grid(row=0, column=0)
        confirm_envs = Button(left_frame, text='Calculate entropy in selected environments and add to results table', command=self.calculate_entropy)
        confirm_envs.grid(row=0, column=1)
        self.start_new_envs = Button(left_frame, text='Destroy results table', command=self.destroy_entropy_results_table)
        self.start_new_envs.grid(row=0, column=2)
        self.start_new_envs.config(state=DISABLED)
        left_frame.pack(side=LEFT, expand=True)#grid(row=0, column=0, sticky=W)

        right_frame = Frame(button_frame)
        previous_step = Button(right_frame, text='Previous step', command=self.entropy_go_back)
        previous_step.grid(row=0, column=0, sticky=E)
        cancel_button = Button(right_frame, text='Cancel', command=self.entropy_screen.destroy)
        cancel_button.grid(row=0, column=1, sticky=E)
        right_frame.pack(side=RIGHT, expand=True)#(row=0, column=10, sticky=E)

        button_frame.grid(row=1,column=0)

        selected_envs_frame = Frame(self.entropy_screen)
        selected_envs_frame.grid(row=0, column=1)
        selected_envs_label = Label(selected_envs_frame, text='Environments created so far:')
        selected_envs_label.grid()
        self.selected_envs_list = Listbox(selected_envs_frame)
        self.selected_envs_list.configure(width=40)
        self.selected_envs_list.grid()
        remove_env_button = Button(selected_envs_frame, text='Remove selected environment', command=self.remove_entropy_env)
        remove_env_button.grid()
        clear_envs = Button(selected_envs_frame, text='Remove all environments', command=lambda x=0:self.selected_envs_list.delete(x,END))
        clear_envs.grid()

    def entropy_go_back(self):
        self.entropy_screen.destroy()
        self.entropy_main_screen.deiconify()
        self.entropy_main_screen.focus()

    def remove_entropy_env(self):
        env = self.selected_envs_list.curselection()
        if env:
            self.selected_envs_list.delete(env)

    def confirm_entropy_options(self):
        lhs_features_chosen = self.lhs_selected_list.get(0)
        lhs_seg_chosen = self.lhs_seg_entry.get()
        rhs_features_chosen = self.rhs_selected_list.get(0)
        rhs_seg_chosen = self.rhs_seg_entry.get()
        if (lhs_features_chosen and lhs_seg_chosen) or (rhs_features_chosen and rhs_seg_chosen):
            MessageBox.showerror(message='You have selected both features and segments for an environment. Please enter only one and clear the other.')
            return


        elif (not lhs_features_chosen) and (not lhs_seg_chosen) and (not rhs_features_chosen) and (not rhs_seg_chosen):
            #allow for no input on one side or the other, but not both
            MessageBox.showerror(message='Both sides of the environment are blank. Construct at least one side.')
            return

        formatted_env = list()

        if lhs_features_chosen:
            lhs_features = self.lhs_selected_list.get(0,END)
            formatted_env.append('[{}]'.format(','.join(lhs_features)))
            #self.selected_envs_list.insert(END,lhs_features)
            self.lhs_selected_list.delete(0,END)

        elif lhs_seg_chosen:
            lhs_seg = self.lhs_seg_entry.get()
            formatted_env.append(lhs_seg)
            #self.selected_envs_list.insert(END,lhs_seg)
            self.lhs_seg_entry.delete(0,END)

        else:
            formatted_env.append('')

        if rhs_features_chosen:
            rhs_features = self.rhs_selected_list.get(0,END)
            formatted_env.append('[{}]'.format(','.join(rhs_features)))
            #self.selected_envs_list.insert(END,rhs_features)
            self.rhs_selected_list.delete(0,END)

        elif rhs_seg_chosen:
            rhs_seg = self.rhs_seg_entry.get()
            formatted_env.append(rhs_seg)
            #self.selected_envs_list.insert(END,rhs_seg)
            self.rhs_seg_entry.delete(0,END)

        else:
            formatted_env.append('')

        formatted_env = '_'.join(formatted_env)
        self.selected_envs_list.insert(END,formatted_env)

    def check_for_uniquess_and_exhuastivity(self, missing_words, overlapping_words, env_list):

        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()

        if self.entropy_uniqueness_var.get() and overlapping_words:
            #envs are exhastive, but some overlap
            final = os.path.split(self.entropy_filename_var.get())[-1]
            filename = 'overlapping_envs_'+final
            with open(os.path.join(self.errors_dir, filename), mode='w', encoding='utf-8') as f:

                print('The environments you selected are not unique, which means that some of them pick out the same environment in the same words.\r\n', file=f)
                print('For example, the environments of \'_[-voice]\' and \'_k\', are not unique. They overlap with each other, since /k/ is [-voice].\r\n',file=f)
                print('When your environments are not unique, the entropy calculation will be inaccurate, since some environments will be counted more than once.\r\n', file=f)
                print('This file contains all the words where this problem could arise.\r\n\r\n', file=f)
                print('Segments you selected: {}, {}\r'.format(seg1, seg2), file=f)
                print('Environments you selected: {}\r'.format(' ,'.join(str(env) for env in env_list)), file=f)
                print('Word\tRelevant environments (segmental level only)\r',file=f)
                for word in overlapping_words:
                    print('{}\t{}\r\n'.format(word,','.join([w for w in overlapping_words[word]])), file=f)

            text1 = 'Your environments are not unique, and two or more of them overlap.'
            text2 = 'This means that some environments will be counted more than once and your entropy values will not be reliable.'
            text3 = 'A text file called {} explaining this problem has been placed in your ERRORS folder ({})'.format(filename,self.errors_dir)
            text4 = 'Do you want to carry on with the entropy calculation anyway?'
            do_entropy = MessageBox.askyesno(message='\n'.join([text1,text2,text3,text4]))
            if not do_entropy:
                return False

        if self.entropy_exhaustive_var.get() and missing_words:
            #environments are unique but non-exhaustive
            filename = 'missing_words_entropy_{}_and_{}.txt'.format(self.seg1_var.get(), self.seg2_var.get())
            with open(os.path.join(self.errors_dir, filename), mode='w', encoding='utf-8') as f:

                print('The following words have at least one of the segments you are searching for, but it occurs in an environment not included in the list you selected\r', file=f)
                print('Segments you selected: {}, {}\r'.format(seg1, seg2), file=f)
                print('Environments you selected: {}\r'.format(' ,'.join(str(env) for env in env_list)), file=f)
                print('Word\tRelevant environments (segmental level only)\r',file=f)
                for word in missing_words:
                    line = '{}\t{}\r'.format(word, ','.join(str(wm) for wm in missing_words[word]))
                    print(line, file=f)

            if self.entropy_uniqueness_var.get() and overlapping_words:
                also = ' also '
            else:
                also = ' '
            text = 'Your selection of environments was{}non-exhaustive.'.format(also)
            text2 = 'This means some words contain the segments you selected, but they do not contain the environments you selected.'
            text3 = 'These words have been printed to the file {} in your ERRORS folder ({}).'.format(filename,self.errors_dir)
            text4 = 'If you choose to carry on with the calculation, then environment-specific entropies will be accurate.'
            text5 = 'However, the weighted average entropy will not reflect the occurrence of the sounds in the non-included environments.'
            if self.entropy_uniqueness_var.get() and overlapping_words:
                text6 = 'The average will also not be accurate because your environments are non-unique.\nWould you still like to calculate entropy in the enviroments you supplied?'
            else:
                text6 = 'Would you still like to calculate entropy in the enviroments you supplied?'
            do_entropy = MessageBox.askyesno(message='\n\r'.join([text, text2, text3, text4, text5, text6]))
            if not do_entropy:
                return False

        #if we made it this far, the user has agreed with everything
        #or else there were no problems to begin with
        return True

    def destroy_entropy_results_table(self):
        try:
            self.entropy_result_list.destroy()
            self.entropy_result_list = None
            self.calculating_entropy_screen.destroy()
            self.calculating_entropy_screen = None
            self.start_new_envs.config(state=DISABLED)
        except (TclError, AttributeError):#widgets don't exist anyway
            pass

    def calculate_entropy(self):
        check = self.selected_envs_list.get(0)
        if not check:
            MessageBox.showwarning(message='Please construct at least one environment')
            return

        if self.calculating_entropy_screen is None:
            self.calculating_entropy_screen = Toplevel()
            self.calculating_entropy_screen.title('Predictability of distribution results')

        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()
        count_what = self.entropy_typetoken_var.get()

        env_list = [env for env in self.selected_envs_list.get(0,END)]
        env_matches, missing_words, overlapping_words = self.calculate_H(seg1,seg2,env_list)
        do_entropy = self.check_for_uniquess_and_exhuastivity(missing_words, overlapping_words,env_list)
        if not do_entropy:
            return #user does not want to see the results

        #at this point there are either no problems
        #or else the user wants to see the results anyway
        if self.entropy_result_list is None:
            self.entropy_result_list = MultiListbox(self.calculating_entropy_screen,
                                    [('Corpus', 10),
                                    ('Tier', 15),
                                    ('Sound1', 10),
                                    ('Sound2', 10),
                                    ('Environment',30),
                                    ('Frequency of Sound1', 10),
                                    ('Frequency of Sound2', 10),
                                    ('Total count',10),
                                    ('Entropy',10)])
        #this is created and all the results are placed into it, but it is not
        #gridded until the corpus as passed both the uniqueness and exhausitivity
        #checks and/or the user has agreed it is OK if it doesn't pass the checks
        self.calculating_entropy_screen.protocol('WM_DELETE_WINDOW', self.destroy_entropy_results_table)
        H_dict = dict()
        output_file_path = os.path.join(os.getcwd(), self.entropy_filename_var.get())
        for env in env_matches:
            total_tokens = sum(env_matches[env][seg1]) + sum(env_matches[env][seg2])
            if not total_tokens:
                H_dict[env] = (0,0)
                data = [self.corpus.name,
                        self.entropy_tier_var.get(),
                        seg1,
                        seg2,
                        env,
                        str(sum(env_matches[env][seg1])),
                        str(sum(env_matches[env][seg2])),
                        str(total_tokens),
                        'N/A']
                self.entropy_result_list.insert(END,data)
            else:
                seg1_prob = sum(env_matches[env][seg1])/total_tokens
                seg2_prob = sum(env_matches[env][seg2])/total_tokens
                seg1_H = log(seg1_prob,2)*seg1_prob if seg1_prob > 0 else 0
                seg2_H = log(seg2_prob,2)*seg2_prob if seg2_prob > 0 else 0
                H = sum([seg1_H, seg2_H])*-1
                if not H:
                    H = H+0
                H_dict[env] = (H, total_tokens)
                data = [self.corpus.name,
                        self.entropy_tier_var.get(),
                        seg1,
                        seg2,
                        env,
                        str(sum(env_matches[env][seg1])),
                        str(sum(env_matches[env][seg2])),
                        str(total_tokens),
                        str(H)]
                self.entropy_result_list.insert(END,data)

        self.entropy_result_list.grid()
        total_frequency = sum(value[1] for value in H_dict.values())
        for env in env_matches:
            H_dict[env] = H_dict[env][0] * (H_dict[env][1] / total_frequency) if total_frequency>0 else 0
        weighted_H = sum(H_dict[env] for env in H_dict)
        total_seg1_matches = sum([sum(env_matches[env][seg1]) for env in env_matches])
        total_seg2_matches = sum([sum(env_matches[env][seg2]) for env in env_matches])
        data = [self.corpus.name,
                    self.entropy_tier_var.get(),
                    seg1,
                    seg2,
                    'AVG',
                    str(total_seg1_matches),
                    str(total_seg2_matches),
                    str(total_seg1_matches+total_seg2_matches),
                    str(weighted_H)]
        self.entropy_result_list.insert(END,data)

       #if self.calculating_entropy_screen is not None:
        print_frame = Frame(self.calculating_entropy_screen)
        print_button = Button(print_frame, text='Save results to file', command=self.print_entropy_results)
        print_button.grid()
        print_frame.grid()
        self.start_new_envs.config(state=ACTIVE)

    def print_entropy_results(self):

        output_file_path = self.suggest_entropy_filename()
        if not output_file_path:
            return

        results = self.entropy_result_list.get(0,END)
        with open(output_file_path, mode='w', encoding='utf-8') as f:
            print('\t'.join(['Corpus', 'Tier', 'Sound1', 'Sound2',
                                'Environment', 'Frequency of Sound1',
                                'Frequency of Sound2', 'Total count','Entropy']),
                                file=f)
            for result in zip(*results):
                print('\t'.join(result), file=f)

    def calculate_H(self, seg1, seg2, user_supplied_envs):

        count_what = self.entropy_typetoken_var.get()
        user_supplied_envs = [self.formalize_env(env) for env in user_supplied_envs]
        env_matches = {'{}_{}'.format(user_env[0],user_env[1]):{seg1:[0], seg2:[0]} for user_env in user_supplied_envs}
        tier_name = self.entropy_tier_var.get()
        words_with_missing_envs = collections.defaultdict(list)
        words_with_overlapping_envs = collections.defaultdict(list)

        for word in self.corpus:
            word.set_string(tier_name) #this makes sure we loop over the right thing
            for pos,seg in enumerate(word):
                if not (seg == seg1 or seg == seg2):
                    continue

                word_env = word.get_env(pos)
                found_env_match = list()
                for user_env in user_supplied_envs:
                    key = '{}_{}'.format(user_env[0],user_env[1])
                    if self.match_to_env(word_env,user_env):
                        if count_what == 'type':
                            value = 1
                        elif count_what == 'token':
                            value = word.abs_freq
                        if seg == seg1:
                            env_matches[key][seg1].append(value)
                            #print(env_matches[key][seg1])
                        else:
                            #print('matched seg {} in word {}'.format(seg1, word))
                            env_matches[key][seg2].append(value)
                        found_env_match.append(user_env)

                if not found_env_match:
                    #found and environemnts with segs the user wants, but in
                    #an environement that was not supplied. Alert the user
                    #about this later
                    words_with_missing_envs[word.spelling].append(str(word_env))

                elif len(found_env_match) > 1:
                    #the user supplied environmnets that overlap, e.g. they want
                    #_[-voice] and also _k, but we shouldn't count this twice
                    #alert the user about this later
                    words_with_overlapping_envs[word.spelling].extend([str(env) for env in found_env_match])

        return env_matches, words_with_missing_envs, words_with_overlapping_envs


    def match_to_env(self,word_env,user_env):

        lhs,rhs = user_env
        l_match = False
        r_match = False

        if not lhs:
            l_match = True
            #empty side is a wildcard, so an automatic matches
        elif type(lhs)==str:
            if lhs == word_env.lhs.symbol:
                l_match = True
        else: #it's a feature list
            for feature in lhs:
                try:
                    match = feature[0] == word_env.lhs.features[feature[1:]]
                except KeyError:
                    break
                if not match:
                    break
            else:
                l_match = True
            #if all([word_env.lhs.features[feature]==lhs[feature] for feature in lhs]):
             #   l_match = True

        if not rhs:
            r_match = True
            #empty sides is a wildcard, so an automatic matches
        elif type(rhs)==str:
            if rhs == word_env.rhs.symbol:
                r_match = True
        else: #it's a feature list
            for feature in rhs:
                try:
                    match = feature[0] == word_env.rhs.features[feature[1:]]
                except KeyError:
                    break #occurs with word bounarires and other non-segmental things
                if not match:
                    break
            else:
                r_match = True
            #if all([word_env.rhs.features[feature]==rhs[feature] for feature in rhs]):
             #   r_match = True

        if l_match and r_match:
            #print('YEAH match for word {} on tier {}'.format(word.spelling, word_env))
            return True
        else:
            return False


    def formalize_env(self,env):

        #there's a problem where some feature names have underscores in them
        #so doing lhs,rhs=env.split('_') causes unpacking problems
        #this in an awakward work-around that checks to see if either side of
        #the environment is a list of features, by looking for brackets, then
        #splits by brackets if necessary. However, I can't split out any
        #starting brackets [ because I also use those for identifying lists
        #at a later point
        #otherwise, if its just segment envrionments, split by underscore

        if ']_[' in env:
            #both sides are lists
            lhs, rhs = env.split(']_')
        elif '_[' in env:
            #only the right hand side is a list of a features
            lhs, rhs = env.split('_', maxsplit=1)
        elif ']_' in env:
            #only the left hand side is a list of features
            lhs, rhs = env.split(']_')
        else: #both sides are segments
            lhs, rhs = env.split('_')

        if not lhs:
            pass
        elif lhs.startswith('['):
            lhs = lhs.lstrip('[')
            lhs = lhs.rstrip(']')
            #lhs = {feature[1:]:feature[0] for feature in lhs.split(',')}
            lhs = lhs.split(',')
        #else it's a segment, just leave it as the string it already is

        if not rhs:
            pass
        elif rhs.startswith('['):
            rhs = rhs.lstrip('[')
            rhs = rhs.rstrip(']')
            #rhs = {feature[1:]:feature[0] for feature in rhs.split(',')}
            rhs = rhs.split(',')
        #else it's a segment, just leave it as the string it already is

        #env = corpustools.Environment(lhs, rhs)
        return (lhs,rhs)

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

        #if as_missing_deps:
        #    MessageBox.showerror(message=('Missing dependencies for either \'numpy\', \'scipy\' or both.'
        #    '\nAcoustic similarity cannot be run without both of them installed.'))
        #    return
        self.as_popup = ASFunction()
        

    @check_for_empty_corpus
    def functional_load(self):

        self.fl_popup = Toplevel()
        self.fl_popup.title('Functional load')
        ipa_frame = LabelFrame(self.fl_popup, text='Sounds')
        segs = [seg.symbol for seg in self.corpus.inventory]
        segs.sort()
        seg1_frame = LabelFrame(ipa_frame, text='Choose first symbol')
        colmax = 10
        col = 0
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(seg1_frame, text=seg, variable=self.fl_seg1_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        seg1_frame.grid()

        seg2_frame = LabelFrame(ipa_frame, text='Choose second symbol')
        colmax = 10
        col = 0
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(seg2_frame, text=seg, variable=self.fl_seg2_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        seg2_frame.grid()

        type_frame = LabelFrame(self.fl_popup, text='Type of functional load to calculate')
        min_pairs_type = Radiobutton(type_frame, text='Minimal pairs',
                                variable=self.fl_type_var, value='min_pairs',
                                command= lambda x=True:self.show_min_pairs_options(x))
        min_pairs_type.grid(sticky=W)
        h_type = Radiobutton(type_frame, text='Change in Entropy',
                            variable=self.fl_type_var, value='h',
                            command= lambda x=False:self.show_min_pairs_options(x))
        h_type.grid(sticky=W)


        min_freq_frame = LabelFrame(self.fl_popup, text='Minimum frequency?')
        fl_frequency_cutoff_label = Label(min_freq_frame, text='Only consider words with frequency of at least...')
        fl_frequency_cutoff_label.grid(row=0, column=0)
        fl_frequency_cutoff_entry = Entry(min_freq_frame, textvariable=self.fl_frequency_cutoff_var)
        fl_frequency_cutoff_entry.delete(0,END)
        fl_frequency_cutoff_entry.insert(0,'0')
        fl_frequency_cutoff_entry.grid(row=0, column=1)
        min_freq_frame.grid(sticky=W)

        self.fl_min_pairs_option_frame = LabelFrame(self.fl_popup, text='Options')
        relative_count_frame = LabelFrame(self.fl_min_pairs_option_frame, text='Relative count?')
        relative_count = Radiobutton(relative_count_frame, text='Calculate minimal pairs relative to corpus size',
                                    value='relative', variable=self.fl_relative_count_var)
        relative_count.grid(sticky=W)
        relative_count.invoke()
        raw_count = Radiobutton(relative_count_frame, text='Calculate just the raw number of minimal pairs',
                                    value='raw', variable=self.fl_relative_count_var)
        raw_count.grid(sticky=W)
        relative_count_frame.grid(sticky=W)

        homophones_frame = LabelFrame(self.fl_min_pairs_option_frame, text='What to do with homophones?')
        count_homophones_button = Radiobutton(homophones_frame, text='Include homophones',
                                    value='include', variable=self.fl_homophones_var)
        count_homophones_button.grid(sticky=W)
        ignore_homophones_button = Radiobutton(homophones_frame,
                                text='Ignore homophones (i.e. count each phonological form once)',
                                value = 'ignore', variable=self.fl_homophones_var)
        ignore_homophones_button.grid(sticky=W)
        ignore_homophones_button.invoke()
        homophones_frame.grid(sticky=W)

        type_frame.grid(row=0, column=0, sticky=(N,W))
        ipa_frame.grid(row=0,column=1, sticky=N)
        self.fl_min_pairs_option_frame.grid(row=0,column=2,sticky=N)
        min_pairs_type.invoke()
        #this has to be invoked much later than it is created because this
        #calls a function that refers to widgets that have not yet been created

        button_frame = Frame(self.fl_popup)
        ok_button = Button(button_frame, text='Calculate functional load\n(start new results table)', command=lambda x=False:self.calculate_functional_load(update=x))
        ok_button.grid(row=0, column=0)
        self.update_fl_button = Button(button_frame, text='Calculate functional load\n(add to current results table)', command=lambda x=True:self.calculate_functional_load(update=x))
        self.update_fl_button.grid()
        self.update_fl_button.config(state=DISABLED)
        cancel_button = Button(button_frame, text='Cancel', command=self.cancel_functional_load)
        cancel_button.grid(row=0, column=1)
        about = Button(button_frame, text='About this function...', command=self.about_functional_load)
        about.grid(row=0, column=2)
        button_frame.grid()

    def show_min_pairs_options(self,visible):
        if visible:
            state = ACTIVE
        if not visible:
            state = DISABLED

        for frame in self.fl_min_pairs_option_frame.winfo_children():
            for widget in frame.winfo_children():
                try:
                    widget.configure(state=state)
                except TclError:
                    pass

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

    def cancel_functional_load(self):
        self.delete_fl_results_table()
        self.fl_popup.destroy()

    def about_functional_load(self):
        about_fl = Toplevel()
        about_fl.title('Functional load')
        desc_frame = LabelFrame(about_fl, text='Brief description')
        desc_label = Label(desc_frame, text='This function calculates the functional load of the contrast between any two segments, based on either the number of minimal pairs or the change in entropy resulting from merging that contrast.')
        desc_label.grid()
        desc_frame.grid(sticky=W)
        source_frame = LabelFrame(about_fl, text='Original sources')

        source_label = Label(source_frame, text='Surendran, Dinoj & Partha Niyogi. 2003. Measuring the functional load of phonological contrasts. In Tech. Rep. No. TR-2003-12.')
        source_label.grid()
        source_label2 = Label(source_frame, text='Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013. High functional load inhibits phonological contrast loss: A corpus study. Cognition 128.179-86')
        source_label2.grid()
        source_frame.grid(sticky=W)
        coder_frame = LabelFrame(about_fl, text='Coded by')
        coder_label = Label(coder_frame, text='Blake Allen')
        coder_label.grid()
        coder_frame.grid(sticky=W)

    def calculate_functional_load(self,update=False):
        if not self.fl_seg1_var.get() or not self.fl_seg2_var.get():
            MessageBox.showwarning(message='Please select two segments.')
            return

        if not update and self.fl_results_table is not None:
            carryon = MessageBox.askyesno(message='You have functional load results open in a table already.\nWould you like to start a new table?')
            if not carryon:
                return
            else:
                self.fl_results_table.destroy()
                self.fl_results.destroy()

        s1 = self.fl_seg1_var.get()
        s2 = self.fl_seg2_var.get()
        frequency_cutoff = int(self.fl_frequency_cutoff_var.get())
        relative_count = True if self.fl_relative_count_var.get() == 'relative' else False
        distinguish_homophones = True if self.fl_homophones_var.get() == 'include' else False
        if self.fl_type_var.get() == 'min_pairs':
            functional_load_thread = ThreadedTask(self.fl_q,
                                    target=FL.minpair_fl,
                                    args=(self.corpus,(s1, s2)),
                                    kwargs={'frequency_cutoff':frequency_cutoff,
                                    'relative_count':relative_count,
                                    'distinguish_homophones':distinguish_homophones,
                                    'threaded_q':self.fl_q})
        else:
            functional_load_thread = ThreadedTask(self.fl_q,
                                    target=FL.deltah_fl,
                                    args=(self.corpus,(s1, s2)),
                                    kwargs={'frequency_measure':'type',
                                            'threaded_q':self.fl_q})
        functional_load_thread.start()
        self.process_fl_queue(update)


    def process_fl_queue(self,update):
        try:
            result = self.fl_q.get(0)
            if update:
                self.update_fl_results(result) #results window exists, just return a new value
            else:
                self.show_fl_result(result) #construct a new window to display results

        except queue.Empty:
            self.fl_popup.after(100, lambda x=update:self.process_fl_queue(update))

    def delete_fl_results_table(self):

        #clean-up function
        if self.fl_results_table is not None:
            self.fl_results_table.destroy()
            self.fl_results_table = None
            self.fl_results.destroy()
        try:
            self.update_fl_button.config(state=DISABLED)
        except TclError:
            pass #the button doesn't exist, ignore the error

    def show_fl_result(self, result):
        self.fl_results = Toplevel()
        self.fl_results.protocol('WM_DELETE_WINDOW', self.delete_fl_results_table)
        self.update_fl_button.config(state=ACTIVE)
        self.fl_results.title('Functional load results')
        if self.fl_type_var.get() == 'min_pairs':
            fl_type = 'Minimal pairs'
            ignored_homophones = 'Yes' if self.fl_homophones_var.get() == 'ignore' else 'No'
            relative_count = 'Yes' if self.fl_relative_count_var.get() == 'relative' else 'No'
        else:
            fl_type = 'Entropy'
            ignored_homophones = 'N/A'
            relative_count = 'N/A'

        self.fl_results_table = MultiListbox(self.fl_results,[('Segment 1',10),
                                                ('Segment 2',10),
                                                ('Type of funcational load', 10),
                                                ('Result',20),
                                                ('Ignored homophones?',5),
                                                ('Relative count?',5),
                                                ('Minimum word frequency', 10)])
        self.fl_results_table.grid()
        self.fl_results_table.insert(END,[self.fl_seg1_var.get(),
                                            self.fl_seg2_var.get(),
                                            fl_type,
                                            result,
                                            ignored_homophones,
                                            relative_count,
                                            self.fl_frequency_cutoff_var.get()])

        button_frame = Frame(self.fl_results)
        print_button = Button(button_frame, text='Save results to file', command=self.print_fl_results)
        print_button.grid(row=0, column=0)
        close_button = Button(button_frame, text='Close this table', command=self.delete_fl_results_table)
        close_button.grid(row=0, column=1)
        button_frame.grid()

    def print_fl_results(self):
        filename = FileDialog.asksaveasfilename()
        if not filename.endswith('.txt'):
            filename += '.txt'
        with open(filename, mode='w', encoding='utf-8') as f:
            print('\t'.join([h for h in self.fl_results_table.headers]), file=f)
            for result in zip(*self.fl_results_table.get(0)):
                print('\t'.join(str(r) for r in result)+'\r\n', file=f)

    def update_fl_results(self, result):
        if self.fl_type_var.get() == 'min_pairs':
            fl_type = 'Minimal pairs'
            ignored_homophones = 'Yes' if self.fl_homophones_var.get() == 'ignore' else 'No'
            relative_count = 'Yes' if self.fl_relative_count_var.get() == 'relative' else 'No'
        else:
            fl_type = 'Entropy'
            ignored_homophones = 'N/A'
            relative_count = 'N/A'
        self.fl_results_table.insert(END,[self.fl_seg1_var.get(),
                                        self.fl_seg2_var.get(),
                                        fl_type,
                                        result,
                                        ignored_homophones,
                                        relative_count,
                                        self.fl_frequency_cutoff_var.get()])


class ToolTip:
    """
    Michael Lange <klappnase (at) freakmail (dot) de>
    The ToolTip class provides a flexible tooltip widget for Tkinter; it is based on IDLE's ToolTip
    module which unfortunately seems to be broken (at least the version I saw).
    INITIALIZATION OPTIONS:
    anchor :        where the text should be positioned inside the widget, must be on of "n", "s", "e", "w", "nw" and so on;
                    default is "center"
    bd :            borderwidth of the widget; default is 1 (NOTE: don't use "borderwidth" here)
    bg :            background color to use for the widget; default is "lightyellow" (NOTE: don't use "background")
    delay :         time in ms that it takes for the widget to appear on the screen when the mouse pointer has
                    entered the parent widget; default is 1500
    fg :            foreground (i.e. text) color to use; default is "black" (NOTE: don't use "foreground")
    follow_mouse :  if set to 1 the tooltip will follow the mouse pointer instead of being displayed
                    outside of the parent widget; this may be useful if you want to use tooltips for
                    large widgets like listboxes or canvases; default is 0
    font :          font to use for the widget; default is system specific
    justify :       how multiple lines of text will be aligned, must be "left", "right" or "center"; default is "left"
    padx :          extra space added to the left and right within the widget; default is 4
    pady :          extra space above and below the text; default is 2
    relief :        one of "flat", "ridge", "groove", "raised", "sunken" or "solid"; default is "solid"
    state :         must be "normal" or "disabled"; if set to "disabled" the tooltip will not appear; default is "normal"
    text :          the text that is displayed inside the widget
    textvariable :  if set to an instance of Tkinter.StringVar() the variable's value will be used as text for the widget
    width :         width of the widget; the default is 0, which means that "wraplength" will be used to limit the widgets width
    wraplength :    limits the number of characters in each line; default is 150

    WIDGET METHODS:
    configure(**opts) : change one or more of the widget's options as described above; the changes will take effect the
                        next time the tooltip shows up; NOTE: follow_mouse cannot be changed after widget initialization

    Other widget methods that might be useful if you want to subclass ToolTip:
    enter() :           callback when the mouse pointer enters the parent widget
    leave() :           called when the mouse pointer leaves the parent widget
    motion() :          is called when the mouse pointer moves inside the parent widget if follow_mouse is set to 1 and the
                        tooltip has shown up to continually update the coordinates of the tooltip window
    coords() :          calculates the screen coordinates of the tooltip window
    create_contents() : creates the contents of the tooltip window (by default a Tkinter.Label)
    """
    def __init__(self, master, text='Your text here', delay=500, **opts):
        self.master = master
        self._opts = {'anchor':'center', 'delay':delay,
                      'follow_mouse':0, 'font':None, 'justify':'left',
                      'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,
                      'width':0, 'wraplength':300}
                      #the following options didn't play nice with ttk
                      #and had to be removed
                      #fg, bg, padx, pady, bd
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1

    def configure(self, **opts):
        for key in opts:
            value = opts.get(key)
            if value is not None:
                self._opts[key] = value
            else:
                raise KeyError('{} is not an option for ToolTip'.format(str(value)))

    ##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
    ##----events on the parent widget; override them if you want to change the widget's behavior--##

    def enter(self, event=None):
        self._schedule()

    def leave(self, event=None):
        self._unschedule()
        self._hide()

    def motion(self, event=None):
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))

    ##------the methods that do the work:---------------------------------------------------------##

    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()

    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()

    ##----these methods might be overridden in derived classes:----------------------------------##

    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = Label(self._tipwindow, **opts)
        label.pack()


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
    calcmenu.add_command(label='Calculate predictability of distribution...', command=app.entropy)
    calcmenu.add_command(labe='Calculate functional load...', command=app.functional_load)
    calcmenu.add_command(labe='Calculate acoustic similarity...', command=app.acoustic_sim)
    menubar.add_cascade(label='Analysis', menu=calcmenu)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help...", command=app.donothing)
    helpmenu.add_command(label="About...", command=app.donothing)
    menubar.add_cascade(label="Help", menu=helpmenu)
    root.config(menu=menubar)

