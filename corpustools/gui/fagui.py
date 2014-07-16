import os

from tkinter import (LabelFrame, Label, W, N, Entry, Button, Radiobutton, Listbox,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE)
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue

from corpustools.freqalt.freq_of_alt import Freqor

from corpustools.gui.basegui import (AboutWindow, FunctionWindow,
                    ResultsWindow, InventoryFrame, ThreadedTask, ToolTip)

class FAFunction(FunctionWindow):

    def __init__(self,corpus,master=None,**options):

        super(FAFunction, self).__init__(master=master, **options)

        self.seg1_var = StringVar()
        self.seg2_var = StringVar()
        self.freq_alt_typetoken_var = StringVar()
        self.freq_alt_stringtype_var = StringVar()
        self.freq_alt_min_rel_var = StringVar()
        self.freq_alt_max_rel_var = StringVar()
        self.freq_alt_min_pairs_var = StringVar()
        self.corpus = corpus
        self.results_table = None
        self.title('Frequency of alternation')
        self.focus()

        top_frame = Frame(self)
        inv_frame = LabelFrame(top_frame, text='Select two sounds')
        seg1_frame = InventoryFrame(self.corpus.get_inventory(), self.seg1_var, 'Sound 1', master=inv_frame)
        seg1_frame.grid()
        seg2_frame = InventoryFrame(self.corpus.get_inventory(), self.seg2_var, 'Sound 2', master=inv_frame)
        seg2_frame.grid()
        inv_frame.grid(row=0,column=0,sticky=N,padx=10)

        relator_type_frame = LabelFrame(top_frame, text='Distance metric')
        self.relator_selection = Listbox(relator_type_frame)
        for rtype in ['Khorsi', 'Edit distance', 'Phonological edit distance']:
            self.relator_selection.insert(0, rtype)
        self.relator_selection.grid()
        relator_type_frame.grid(row=0,column=1,sticky=N,padx=10)

        options_frame = LabelFrame(top_frame, text='Options')

        typetoken_frame = LabelFrame(options_frame, text='Type or Token')
        type_button = Radiobutton(typetoken_frame, text='Count types', variable=self.freq_alt_typetoken_var, value='type')
        type_button.grid(sticky=W)
        type_button.invoke()
        token_button = Radiobutton(typetoken_frame, text='Count tokens', variable=self.freq_alt_typetoken_var, value='token')
        token_button.grid(sticky=W)
        if self.corpus.custom and not self.corpus.has_frequency():
            token_button.configure(state=('disabled'))
        typetoken_frame.grid(column=0, row=0, sticky=W)

        stringtype_frame = LabelFrame(options_frame, text='String type')
        spelling_button = Radiobutton(stringtype_frame, text='Compare spelling', variable=self.freq_alt_stringtype_var, value='spelling')
        spelling_button.grid(sticky=W)
        spelling_button.invoke()
        if self.corpus.custom and not self.corpus.has_spelling():
            transcription_button.configure(state=('disabled'))
        transcription_button = Radiobutton(stringtype_frame, text='Compare transcription', variable=self.freq_alt_stringtype_var, value='transcription')
        transcription_button.grid(sticky=W)
        if self.corpus.custom and not self.corpus.has_transcription():
            transcription_button.configure(state=('disabled'))
        stringtype_frame.grid(column=0, row=1, sticky=W)

        min_pairs_frame = LabelFrame(options_frame, text='What to do with minimal pairs')
        ignore_min_pairs = Radiobutton(min_pairs_frame, text='Ignore minimal pairs', variable=self.freq_alt_min_pairs_var, value='ignore')
        ignore_min_pairs.grid()
        include_min_pairs = Radiobutton(min_pairs_frame, text='Include minimal pairs', variable=self.freq_alt_min_pairs_var, value='include')
        include_min_pairs.grid()
        ignore_min_pairs.select()
        min_pairs_frame.grid(column=0,row=2,sticky=W)

        threshold_frame = LabelFrame(options_frame, text='Return only results with similarity between...')
        min_label = Label(threshold_frame, text='Minimum: ')
        min_label.grid(row=0, column=0)
        min_rel_entry = Entry(threshold_frame, textvariable=self.freq_alt_min_rel_var)
        min_rel_entry.grid(row=0, column=1, sticky=W)
        max_label = Label(threshold_frame, text='Maximum: ')
        max_label.grid(row=1, column=0)
        max_rel_entry = Entry(threshold_frame, textvariable=self.freq_alt_max_rel_var)
        max_rel_entry.grid(row=1, column=1, sticky=W)
        threshold_frame.grid(column=0, row=3, sticky=W)

        output_frame = LabelFrame(options_frame, text='Output all alternations to file?')
        label = Label(output_frame, text='Enter a file name (leave blank for no output file)')
        self.output_entry = Entry(output_frame)
        navigate = Button(output_frame, text='Select file location', command=self.choose_output_location)
        label.grid(row=0, column=0, sticky=W)
        self.output_entry.grid(row=1, column=0, sticky=W)
        navigate.grid(row=1, column=1, sticky=W)
        output_frame.grid(column=0,row=4,sticky=W)

        options_frame.grid(row=0, column=2, sticky=N, padx=10)
        top_frame.grid(row=0,column=0)

        bottom_frame = Frame(self)
        ok_button = Button(bottom_frame, text='Calculate alignment\n(start new results table)', command=self.calculate_freq_of_alt)
        ok_button.grid(row=0,column=0)
        self.update_fa_button = Button(bottom_frame, text='Calculate alignment\n(add to current results table)', command=lambda x=True:self.calculate_freq_of_alt(update=x))
        self.update_fa_button.grid(row=0,column=1)
        self.update_fa_button.config(state=DISABLED)
        cancel_button = Button(bottom_frame, text='Cancel', command=self.cancel_freq_of_alt)
        cancel_button.grid(row=0,column=2)
        bottom_frame.grid(row=1,column=0)

    def cancel_freq_of_alt(self):
        self.close_results_table()
        self.destroy()

    def choose_output_location(self):
        filename = FileDialog.asksaveasfilename()
        if filename:
            if not filename.endswith('.txt'):
                filename = filename+'.txt'
            self.output_entry.delete(0,END)
            self.output_entry.insert(0,filename)

    def calculate_freq_of_alt(self, update=False):
        s1 = self.seg1_var.get()
        s2 = self.seg2_var.get()
        if not s1 and s2:
            MessageBox.showerror(message='Please select 2 sounds')
            return
        index = self.relator_selection.curselection()
        if not index:
            MessageBox.showerror(message='Please select a distance metric')
            return
        if not update and self.results_table is not None:
            kill_results = MessageBox.askyesno(message=('You already have a results window open.\n'
                                            'Do you want to destroy it and start a new calculation?'))
            if not kill_results:
                return
            else:
                self.close_results_table()

        relator_type = self.relator_selection.get(index)
        if relator_type == 'Khorsi':
            relator_type = 'khorsi'
        elif relator_type == 'Edit distance':
            relator_type = 'edit_distance'
        elif relator_type == 'Phonological edit distance':
            relator_type = 'phono_edit_distance'

        self.update_fa_button.config(state=ACTIVE)

        string_type = self.freq_alt_stringtype_var.get()
        count_what = self.freq_alt_typetoken_var.get()
        min_ = self.freq_alt_min_rel_var.get()
        min_rel = int(min_) if min_ else None
        max_ = self.freq_alt_max_rel_var.get()
        max_rel = int(max_) if max_ else None
        min_pairs_ok = True if self.freq_alt_min_pairs_var.get() == 'include' else False
        output_file = self.output_entry.get()
        if not output_file:
            outputfile = None

        if not update:
            header = [('Sound 1',20),
                        ('Sound 2', 20),
                        ('Total words in corpus', 10),
                        ('Total words with alternations', 10),
                        ('Frequency of alternation', 10),
                        ('Type or token', 10),
                        ('Distance metric', 10)]
            title = 'Frequency of alternation results'

            freqor = Freqor(self.corpus.name, ready_made_corpus=self.corpus)
            results = freqor.calc_freq_of_alt(s1, s2, relator_type, string_type, count_what, phono_align=True,
                                            min_rel=min_rel, max_rel=max_rel, min_pairs_okay=min_pairs_ok,
                                            from_gui=True, output_filename=output_file)
            self.results_table = ResultsWindow(title, header, delete_method=self.close_results_table)
            self.results_table.update([s1, s2, results[0], results[1], results[2], count_what, relator_type])

        else:
            freqor = Freqor(self.corpus.name, ready_made_corpus=self.corpus)
            results = freqor.calc_freq_of_alt(s1, s2, relator_type, string_type, count_what, phono_align=True,
                                            min_rel=min_rel, max_rel=max_rel, min_pairs_okay=min_pairs_ok,
                                            from_gui=True, output_filename=output_file)
            self.results_table.update([s1, s2, results[0], results[1], results[2], count_what, relator_type])

    def close_results_table(self):
        try:
            self.results_table.destroy()
            self.results_table = None
        except (TclError, AttributeError):
            pass#doesn't exist to be destroyed
        self.update_fa_button.config(state=DISABLED)
