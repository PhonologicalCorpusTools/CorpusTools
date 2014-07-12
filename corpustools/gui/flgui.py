import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE, N)
from tkinter import Radiobutton as OldRadiobutton
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue
import time
import corpustools.funcload.functional_load as FL

from corpustools.gui.basegui import (AboutWindow, FunctionWindow, InventoryFrame,
                    ResultsWindow, MultiListbox, ThreadedTask, ToolTip, Toplevel,
                    ToolTip)


class FLFunction(FunctionWindow):
    def __init__(self,corpus,master=None, **options):
        super(FLFunction, self).__init__(master=master, **options)
        self.corpus = corpus
        #Functional load variables
        self.fl_frequency_cutoff_var = StringVar()
        self.fl_homophones_var = StringVar()
        self.fl_relative_count_var = StringVar()
        self.fl_seg1_var = StringVar()
        self.fl_seg2_var = StringVar()
        self.entropy_pairs_var = StringVar()
        self.fl_q = queue.Queue()
        self.fl_results = None
        self.fl_type_var = StringVar()

        self.title('Functional load')
        ipa_frame = LabelFrame(self, text='Sounds')
        ipa_frame_tip = ToolTip(ipa_frame, text=('Add (a) pair(s) of sounds whose contrast to collapse.'
                                    ' For example, if you\'re interested in the functional load of the [s]'
                                    ' / [z] contrast, you only need to add that pair. If, though, you\'re'
                                    ' interested in the functional load of the voicing contrast among obstruents,'
                                    ' you may need to add (p, b), (t, d), and (k, g).'))
        select_sounds = Button(ipa_frame, text='Add pairs of sounds', command=self.select_sound_pairs)
        select_sounds.grid()
        remove_button = Button(ipa_frame, text='Remove selected sound pair', command=self.remove_sounds)
        remove_button.grid()
        self.sound_list = MultiListbox(ipa_frame, [('Sound 1', 10),('Sound 2', 10)])
        self.sound_list.grid()

        type_frame = LabelFrame(self, text='Type of functional load to calculate')
        min_pairs_type = Radiobutton(type_frame, text='Minimal pairs',
                                variable=self.fl_type_var, value='min_pairs',
                                command= lambda x=True:self.show_min_pairs_options(x))
        min_pairs_tip = ToolTip(min_pairs_type, text=('Calculate the functional load of the'
                        ' contrast between two sets of segments as a count of minimal pairs'
                        ' distinguished by paired segments in the set (e.g. +/-voice obstruent pairs).'
                        ' This is the method used by Wedel et al. (2013).'))
        min_pairs_type.grid(sticky=W)
        h_type = Radiobutton(type_frame, text='Change in Entropy',
                            variable=self.fl_type_var, value='h',
                            command= lambda x=False:self.show_min_pairs_options(x))
        h_type_tip = ToolTip(h_type, text=('Calculate the functional load of the contrast '
                            'between between two sets of segments as the decrease in corpus'
                            ' entropy caused by a merger of paired segments in the set '
                            '(e.g. +/-voice obstruent pairs).'))
        h_type.grid(sticky=W)


        min_freq_frame = LabelFrame(self, text='Minimum frequency?')
        fl_frequency_cutoff_label = Label(min_freq_frame, text='Only consider words with frequency of at least...')
        fl_frequency_cutoff_label.grid(row=0, column=0)
        fl_frequency_cutoff_entry = Entry(min_freq_frame, textvariable=self.fl_frequency_cutoff_var)
        fl_frequency_cutoff_entry.delete(0,END)
        fl_frequency_cutoff_entry.insert(0,'0')
        fl_frequency_cutoff_entry.grid(row=0, column=1)
        min_freq_frame.grid(sticky=W)

        self.fl_min_pairs_option_frame = LabelFrame(self, text='Options')
        seg_pairing_frame = LabelFrame(self.fl_min_pairs_option_frame, text='How to handle multiple segment pairs')
        pairs_together = Radiobutton(seg_pairing_frame, text='Calculate functional load of all segment pairs together',
                                    variable=self.entropy_pairs_var, value='together')
        pairs_together.grid(sticky=W)
        pairs_individually = Radiobutton(seg_pairing_frame, text='Calculate functional load of each segment pair individually',
                                    variable=self.entropy_pairs_var, value='individual')
        pairs_individually.grid(sticky=W)
        pairs_together.select()
        seg_pairing_frame.grid()
        relative_count_frame = LabelFrame(self.fl_min_pairs_option_frame, text='Relative count?')
        options_tip = ToolTip(relative_count_frame, text=('The raw count of minimal pairs will'
                            ' be divided by the number of words that include any of the target segments '
                            'present in the list at the left.'))
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
        count_homophone_tip = ToolTip(count_homophones_button, text=('This setting will overcount alternative'
                            ' spellings of the same word, e.g. axel~actual and axle~actual, '
                            'but will allow you to count e.g. sock~shock twice, once for each'
                            ' meaning of \'sock\' (footwear vs. punch)'))
        count_homophones_button.grid(sticky=W)
        ignore_homophones_button = Radiobutton(homophones_frame,
                                text='Ignore homophones (i.e. count each phonological form once)',
                                value = 'ignore', variable=self.fl_homophones_var)
        ignore_homphones_tip = ToolTip(ignore_homophones_button, text=('This setting will count sock~shock (sock=clothing)'
                            ' and sock~shock (sock=punch) as just one minimal pair, but will avoid overcounting words'
                            ' with spelling variations. This is the version used by Wedel et al. (2013).'))
        ignore_homophones_button.grid(sticky=W)
        ignore_homophones_button.invoke()
        homophones_frame.grid(sticky=W)

        type_frame.grid(row=0, column=0, sticky=(N,W))
        ipa_frame.grid(row=0,column=1, sticky=N)
        self.fl_min_pairs_option_frame.grid(row=0,column=2,sticky=N)
        min_pairs_type.invoke()
        #this has to be invoked much later than it is created because this
        #calls a function that refers to widgets that have not yet been created

        button_frame = Frame(self)
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
        self.focus()

    def select_sound_pairs(self):

        self.select_sounds = Toplevel()
        self.select_sounds.title('Select sounds')
        segs = [seg.symbol for seg in self.corpus.get_inventory()]
        segs.sort()

        sound1_frame = LabelFrame(self.select_sounds, text='First sound')
        self.seg1_frame = InventoryFrame(segs, self.fl_seg1_var, 'Choose first symbol', master=sound1_frame)
        self.seg1_frame.grid()
        sound1_frame.grid()

        sound2_frame = LabelFrame(self.select_sounds, text='Second sound')
        self.seg2_frame = InventoryFrame(segs, self.fl_seg2_var, 'Choose second symbol', master=sound2_frame)
        self.seg2_frame.grid()
        sound2_frame.grid()

        button_frame = Frame(self.select_sounds)
        ok_button = Button(button_frame, text='Add sounds to list', command=self.add_sounds)
        ok_button.grid(sticky=W)
        cancel_button = Button(button_frame, text='Done', command=self.select_sounds.destroy)
        cancel_button.grid(sticky=W)
        button_frame.grid(row=0,column=2)

    def add_sounds(self):
        sound1 = self.fl_seg1_var.get()
        sound2 = self.fl_seg2_var.get()
        if not sound1 or not sound2:
            MessageBox.showwarning('Predictability of distribution', message='Please select 2 sounds')
            return

        self.sound_list.insert(END,[sound1, sound2])
        for widget in self.seg1_frame.winfo_children():
            try:
                widget.deselect()
            except AttributeError:
                pass
        for widget in self.seg2_frame.winfo_children():
            try:
                widget.deselect()
            except AttributeError:
                pass

    def remove_sounds(self):
        selection = self.sound_list.curselection()
        if selection:
            self.sound_list.delete(self.sound_list.curselection())

    def about_functional_load(self):
        about = AboutWindow('Functional load',
                    ('This function calculates the functional load of the contrast'
                    ' between any two segments, based on either the number of minimal'
                    ' pairs or the change in entropy resulting from merging that contrast.'),
                    ['Surendran, Dinoj & Partha Niyogi. 2003. Measuring the functional load of phonological contrasts. In Tech. Rep. No. TR-2003-12.',
                    'Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013. High functional load inhibits phonological contrast loss: A corpus study. Cognition 128.179-86'],
                    ['Blake Allen'])

    def calculate_functional_load(self,update=False):
        if self.sound_list.size() == 0:
            MessageBox.showerror(message='Please select at least one pair of segments')
            return

        if not update and self.fl_results is not None:
            carryon = MessageBox.askyesno(message='You have functional load results open in a table already.\nWould you like to start a new table?')
            if not carryon:
                return
            else:
                self.fl_results.destroy()

        seg_list = self.sound_list.get(0,END)
        seg_pairs = list(zip(seg_list[0], seg_list[1]))
        frequency_cutoff = int(self.fl_frequency_cutoff_var.get())
        relative_count = True if self.fl_relative_count_var.get() == 'relative' else False
        distinguish_homophones = True if self.fl_homophones_var.get() == 'include' else False

        if self.entropy_pairs_var.get() == 'individual':
            target = FL.individual_segpairs_fl
        else:
            target = FL.collapse_segpairs_fl

        if self.fl_type_var.get() == 'min_pairs':
            functional_load_thread = ThreadedTask(self.fl_q,
                                    target=target,
                                    args={},
                                    kwargs={
                                    'corpus':self.corpus,
                                    'segment_pairs':seg_pairs,
                                    'func_type':'min_pairs',
                                    'frequency_cutoff':frequency_cutoff,
                                    'relative_count':relative_count,
                                    'distinguish_homophones':distinguish_homophones,
                                    'threaded_q':self.fl_q})
        else:
            functional_load_thread = ThreadedTask(self.fl_q,
                                    target=target,
                                    args={},
                                    kwargs={
                                    'corpus':self.corpus,
                                    'segment_pairs':seg_pairs,
                                    'func_type':'entropy',
                                    'frequency_cutoff':frequency_cutoff,
                                    'type_or_token':'type',
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
            self.after(100, lambda x=update:self.process_fl_queue(update))

    def delete_fl_results(self):
        #clean-up function
        if self.fl_results is not None:
            self.fl_results.destroy()
            self.fl_results = None

        try:
            self.update_fl_button.config(state=DISABLED)
        except TclError:
            pass #the button doesn't exist, ignore the error

    def show_fl_result(self, result):
        if self.fl_type_var.get() == 'min_pairs':
            fl_type = 'Minimal pairs'
            ignored_homophones = 'Yes' if self.fl_homophones_var.get() == 'ignore' else 'No'
            relative_count = 'Yes' if self.fl_relative_count_var.get() == 'relative' else 'No'
        else:
            fl_type = 'Entropy'
            ignored_homophones = 'N/A'
            relative_count = 'N/A'

        header = [('Segment 1',10),
                ('Segment 2',10),
                ('Type of funcational load', 10),
                ('Result',20),
                ('Ignored homophones?',5),
                ('Relative count?',5),
                ('Minimum word frequency', 10)]
        title = 'Functional load results'
        self.fl_results = ResultsWindow(title,header,delete_method=self.delete_fl_results)
        self.update_fl_button.config(state=ACTIVE)
        self.update_fl_results(result)


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

    def update_fl_results(self, result):
        if self.fl_type_var.get() == 'min_pairs':
            fl_type = 'Minimal pairs'
            ignored_homophones = 'Yes' if self.fl_homophones_var.get() == 'ignore' else 'No'
            relative_count = 'Yes' if self.fl_relative_count_var.get() == 'relative' else 'No'
        else:
            fl_type = 'Entropy'
            ignored_homophones = 'N/A'
            relative_count = 'N/A'
        seg_list = self.sound_list.get(0,END)

        if self.entropy_pairs_var.get() == 'individual':
            for result,seg1,seg2 in zip(result, *seg_list):
                self.fl_results.update([seg1,
                                        seg2,
                                        fl_type,
                                        result,
                                        ignored_homophones,
                                        relative_count,
                                        self.fl_frequency_cutoff_var.get()])
        else:
            seg1 = ','.join(seg_list[0])
            seg2 = ','.join(seg_list[1])
            self.fl_results.update([seg1,
                                        seg2,
                                        fl_type,
                                        result,
                                        ignored_homophones,
                                        relative_count,
                                        self.fl_frequency_cutoff_var.get()])

    def cancel_functional_load(self):
        self.delete_fl_results()
        self.destroy()

