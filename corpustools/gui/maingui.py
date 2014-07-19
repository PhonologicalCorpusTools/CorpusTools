#-------------------------------------------------------------------------------
# Name: module1
# Purpose:
#
# Author: JSMIII
#
# Created: 08/01/2014
# Copyright: (c) JSMIII 2014
# Licence: <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from tkinter import *
from tkinter.ttk import *
from tkinter import Radiobutton as OldRadiobutton
#ttk.Radiobutton doesn't support the indicatoron option, which is used for some
#of the windows
import tkinter.messagebox as MessageBox
import tkinter.filedialog as FileDialog

import threading
import queue
import os
import collections
from codecs import open
from math import log

from corpustools.gui.basegui import (ThreadedTask, MultiListbox, PreferencesWindow, TableView,
                                    CONFIG_PATH, DEFAULT_DATA_DIR, LOG_DIR, ERROR_DIR,config)
try:
    from corpustools.gui.asgui import ASFunction
    as_enabled = True
except ImportError:
    as_enabled = False
from corpustools.gui.ssgui import SSFunction
from corpustools.gui.flgui import FLFunction
from corpustools.gui.pdgui import PDFunction
from corpustools.gui.fagui import FAFunction
from corpustools.gui.corpusgui import (CorpusManager, FeatureSystemManager,
                                    EditFeatureSystemWindow, save_binary,
                                    export_corpus_csv,export_feature_matrix_csv)

#try:
#    from PIL import Image as PIL_Image
#    from PIL import ImageTk as PIL_ImageTk
#    use_logo = True
#except ImportError:
#    use_logo = False





class GUI(Toplevel):

    def __init__(self,master):
        self.show_warnings = BooleanVar()
        self.show_tooltips = BooleanVar()

        self.show_warnings.set(True)
        self.show_tooltips.set(True)
        self.load_config()

        #Set up logging
        self.log_dir = LOG_DIR
        self.errors_dir = ERROR_DIR

        #NON-TKINTER VARIABLES
        self.master = master
        self.corpus = None
        #user defined features systems are added automatically at a later point
        self.warn_about_changes = False

        #TKINTER VARIABLES ("globals")
        #main screen variabls
        self.corpus_report_label_var = StringVar()
        self.corpus_report_label_var.set('0 words loaded from corpus')
        self.corpus_button_var = StringVar()
        self.features_button_var = StringVar()
        self.search_var = StringVar()

        #corpus information variables
        self.corpus_var = StringVar()
        self.corpus_var.set('No corpus selected')
        self.corpus_size_var = IntVar()
        self.corpus_size_var.set(0)


        #MAIN SCREEN STUFF
        self.main_screen = Frame(master)
        self.main_screen.pack(expand=True,fill='both')
        self.info_frame = Frame(self.main_screen)
        self.info_frame.pack()

        #self.corpus_table = TableView(self.main_screen)
        #self.corpus_table.grid()

        corpus_info_label = Label(self.info_frame ,text='Corpus: No corpus selected')#textvariable=self.corpus_var)
        corpus_info_label.grid()
        size_info_label = Label(self.info_frame, text='Size: No corpus selected')#textvariable=self.corpus_size_var)
        size_info_label.grid()
        feature_info_label = Label(self.info_frame, text='Feature system: No corpus selected')
        feature_info_label.grid()
        self.corpus_frame = Frame(self.main_screen)
        self.corpus_frame.pack(expand=True,fill='both')

        #Splash image at start-up
        #try:
        #    self.splash_image_path = os.path.join(base_path,'logo.jpg')
        #    self.splash_canvas = Canvas(self.corpus_frame)
        #    self.splash_canvas['width'] = '323'
        #    self.splash_canvas['height'] = '362'
        #    image = PIL_Image.open(self.splash_image_path)
        #    self.splash_image = PIL_ImageTk.PhotoImage(image,master=self.splash_canvas)
        #    self.splash_canvas.create_image(0,0,anchor=NW,image=self.splash_image)
        #    self.splash_canvas.grid()
        #except:
        #    pass#if the image file is not found, then don't bother

    def load_corpus(self):
        corpusload = CorpusManager()
        corpusload.top.wait_window()
        self.corpus = corpusload.get_corpus()
        if self.corpus is not None:
            self.main_screen_refresh()

    def load_feature_matrices(self):
        matrixload = FeatureSystemManager()
        matrixload.top.wait_window()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            config.read(CONFIG_PATH)
        else:
            config['storage'] = {'directory' : DEFAULT_DATA_DIR}
            with open(CONFIG_PATH,'w') as configfile:
                config.write(configfile)
        data_dir = config['storage']['directory']
        feature_dir = os.path.join(data_dir,'FEATURE')
        if not os.path.exists(feature_dir):
            os.makedirs(feature_dir)

        corpus_dir = os.path.join(data_dir,'CORPUS')
        if not os.path.exists(corpus_dir):
            os.makedirs(corpus_dir)

    def check_for_valid_corpus(function):
        def do_check(self):
            missing = list()
            if self.corpus.is_custom():
                if not self.corpus.has_spelling():
                    missing.append('spelling')
                if not self.corpus.has_transcription():
                    missing.append('transcription')
                if not self.corpus.has_frequency():
                    missing.append('token frequency')
                if self.show_warnings.get() and missing:
                    missing = ','.join(missing)
                    MessageBox.showwarning(message='Some information neccessary for this analysis is missing from your corpus: {}\nYou will not be able to select every option'.format(missing))
            function(self)
        return do_check

    def check_for_valid_feature_matrix(function):
        def do_check(self):
            corpus_inventory = self.corpus.get_inventory()
            if self.corpus.has_feature_matrix():
                missing = []
                feature_inventory = self.corpus.get_feature_matrix().get_segments()
                for seg in corpus_inventory:
                    if seg not in feature_inventory:
                        missing.append(str(seg))

                if missing:
                    MessageBox.showerror(message='Some segments in the corpus inventory are not in the feature system.\nPlease go to Options->View/change feature system... to view missing segments and add them.')
                    return
            else:
                MessageBox.showerror(message='Please load a feature system through the View/change feature system in the Options menu.')
                return
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


    @check_for_unsaved_changes
    def quit(self,event=None):
        self.master.quit()


    def show_preferences(self):
        preferences = PreferencesWindow()
        preferences.wait_window()
        self.load_config()

    def update_info_frame(self):
        for child in self.info_frame.winfo_children():
            child.destroy()

        if self.corpus is not None:
            corpus_name = self.corpus.get_name()
            corpus_size = len(self.corpus)
        else:
            corpus_name = "No corpus selected"
            corpus_size = "No corpus selected"

        corpus_info_label = Label(self.info_frame ,text='Corpus: {}'.format(corpus_name))#textvariable=self.corpus_var)
        corpus_info_label.grid()

        size_info_label = Label(self.info_frame, text='Size: {}'.format(corpus_size))#textvariable=self.corpus_size_var)
        size_info_label.grid()

        if self.corpus.has_feature_matrix():
            system_name = self.corpus.get_feature_matrix().get_name()
        else:
            system_name = 'None'

        feature_info_label = Label(self.info_frame, text='Feature system: {}'.format(system_name))#textvariable=self.feature_system_var)
        feature_info_label.grid()


    def issue_changes_warning(self):
        if not self.warn_about_changes:
            return
        should_quit = MessageBox.askyesno(message=(
        'You have made changes to your corpus, but you haven\'t saved it. You will lose these changes if you load a new corpus now.\n Do you want to continue?'))
        return should_quit


    @check_for_empty_corpus
    def search(self):

        self.search_popup = Toplevel()
        self.search_popup.title('Search {}'.format(self.corpus.get_name()))
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
    @check_for_valid_feature_matrix
    def string_similarity(self):
        sspopup = SSFunction(self.corpus, show_tooltips = self.show_tooltips.get())

    def donothing(self,event=None):
        pass

    @check_for_empty_corpus
    def save_corpus(self):
        """
        pickles the corpus, which makes loading it WAY easier
        would be nice to have an option to save as pickle and also "export as"
        a .txt/csv file
        """
        save_binary(self.corpus,os.path.join(
                        config['storage']['directory'],'CORPUS',
                        self.corpus.get_name()+'.corpus'))
        self.warn_about_changes = False
        MessageBox.showinfo(message='Save successful!')

    def main_screen_refresh(self):
        #self.update_info_frame()
        #self.corpus_table.load_corpus(self.corpus)

        for child in self.corpus_frame.winfo_children():
            child.pack_forget()
        random_word = self.corpus.random_word()
        headers = [d for d in random_word.descriptors if not d is None or not d == '']
        rows = [[getattr(word,d,'???') for d in word.descriptors] for word in self.corpus.iter_sort()]
        self.corpus_box = TableView(self.corpus_frame, headers,rows)
        self.update_info_frame()
        self.corpus_box.pack(expand=True,fill='both')


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
        if target and self.show_warnings.get():
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
        if self.show_warnings.get():
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
        for seg in self.corpus.get_inventory():
            if seg in ['#','']: #wtf?
                continue
            if all(feature[0] == self.corpus.specifier[seg.symbol,feature[1:]] for feature in features):
                matches.append(seg)

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
            matches = ' '.join(map(str,m))

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

    @check_for_empty_corpus
    @check_for_valid_corpus
    @check_for_valid_feature_matrix
    def prod(self,shortcut=None):
        pd_popup = PDFunction(self.corpus, show_tooltips = self.show_tooltips.get())


    @check_for_empty_corpus
    @check_for_valid_corpus
    @check_for_valid_feature_matrix
    def frequency_of_alternation(self):
        fa_popup = FAFunction(self.corpus, show_tooltips = self.show_tooltips.get())

    @check_for_empty_corpus
    def show_feature_system(self):
        if self.show_warnings.get():
            word = self.corpus.random_word()
            if word.tiers:
                msg = ('You have already created tiers based on a feature system.'
                        '\nChanging feature systems may give unexpected results'
                        ' and is not recommended.')
                MessageBox.showwarning(message=msg)



        feature_screen = EditFeatureSystemWindow(self.corpus)
        feature_screen.top.wait_window()
        if feature_screen.change:
            self.corpus.set_feature_matrix(feature_screen.get_feature_matrix())
        self.main_screen_refresh()


    def acoustic_sim(self):

        if not as_enabled:
            MessageBox.showerror(message=('Missing dependencies for either \'numpy\', \'scipy\' or both.'
            '\nAcoustic similarity cannot be run without both of them installed.'))
            return
        self.as_popup = ASFunction(show_tooltips = self.show_tooltips.get())


    @check_for_empty_corpus
    @check_for_valid_corpus
    @check_for_valid_feature_matrix
    def functional_load(self):
        fl_popup = FLFunction(self.corpus, show_tooltips = self.show_tooltips.get())


    @check_for_empty_corpus
    def export_corpus_to_text_file(self):
        filename = FileDialog.asksaveasfilename(initialfile = self.corpus.get_name()+'.txt')
        if not filename:
            return

        export_corpus_csv(self.corpus,filename)

    @check_for_empty_corpus
    def export_feature_matrix_to_text_file(self):
        matrix = self.corpus.get_feature_matrix()
        filename = FileDialog.asksaveasfilename(initialfile = matrix.get_name()+'.txt')
        if not filename:
            return

        export_feature_matrix_csv(matrix,filename)



def make_menus(root,app):

    menubar = Menu(root)
    corpusmenu = Menu(menubar, tearoff=0)
    corpusmenu.add_command(label='Load corpus...', command=app.load_corpus)
    corpusmenu.add_command(label='Manage feature systems...', command=app.load_feature_matrices)
    corpusmenu.add_command(label='Save corpus', command=app.save_corpus)
    #corpusmenu.add_command(label='Choose built-in corpus...', command=app.choose_corpus)
    #corpusmenu.add_command(label='Use custom corpus...', command=app.choose_custom_corpus)
    #corpusmenu.add_command(label='Create corpus from text...', command=app.corpus_from_text)
    corpusmenu.add_command(label='Export corpus as text file (use with spreadsheets etc.)...', command=app.export_corpus_to_text_file)
    corpusmenu.add_command(label='Export feature system as text file...', command=app.export_feature_matrix_to_text_file)
    corpusmenu.add_command(label="Quit", command=app.quit, accelerator='Ctrl+Q')
    menubar.add_cascade(label="Corpus", menu=corpusmenu)

    optionmenu = Menu(menubar, tearoff=0)
    #optionmenu.add_command(label='Search corpus...', command=app.search)
    optionmenu.add_command(label='Preferences...', command=app.show_preferences)
    optionmenu.add_command(label='View/change feature system...', command=app.show_feature_system)
    optionmenu.add_command(label='Add Tier...', command=app.create_tier)
    optionmenu.add_command(label='Remove Tier...', command=app.destroy_tier)
    optionmenu.add_checkbutton(label='Show warnings', onvalue=True, offvalue=False, variable=app.show_warnings)
    optionmenu.add_checkbutton(label='Show tooltips', onvalue=True, offvalue=False, variable=app.show_tooltips)
    menubar.add_cascade(label='Options', menu=optionmenu)

    calcmenu = Menu(menubar, tearoff=0)
    calcmenu.add_command(label='Calculate string similarity...', command=app.string_similarity)
    calcmenu.add_command(label='Calculate frequency of alternation...', command=app.frequency_of_alternation)
    calcmenu.add_command(label='Calculate predictability of distribution...', command=app.prod)
    calcmenu.add_command(labe='Calculate functional load...', command=app.functional_load)
    calcmenu.add_command(labe='Calculate acoustic similarity...', command=app.acoustic_sim)
    menubar.add_cascade(label='Analysis', menu=calcmenu)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help...", command=app.donothing)
    helpmenu.add_command(label="About...", command=app.donothing)
    menubar.add_cascade(label="Help", menu=helpmenu)
    root.config(menu=menubar)
