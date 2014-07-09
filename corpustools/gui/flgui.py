import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE, N)
from tkinter import Radiobutton as OldRadiobutton
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue
import corpustools.funcload.functional_load as FL

from corpustools.gui.basegui import (AboutWindow, FunctionWindow,
                    ResultsWindow, MultiListbox, ThreadedTask, ToolTip)


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
        self.fl_q = queue.Queue()
        self.fl_results_table = None
        self.fl_type_var = StringVar()

        self.title('Functional load')
        ipa_frame = LabelFrame(self, text='Sounds')
        segs = [seg.symbol for seg in self.corpus.get_inventory()]
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

        type_frame = LabelFrame(self, text='Type of functional load to calculate')
        min_pairs_type = Radiobutton(type_frame, text='Minimal pairs',
                                variable=self.fl_type_var, value='min_pairs',
                                command= lambda x=True:self.show_min_pairs_options(x))
        min_pairs_type.grid(sticky=W)
        h_type = Radiobutton(type_frame, text='Change in Entropy',
                            variable=self.fl_type_var, value='h',
                            command= lambda x=False:self.show_min_pairs_options(x))
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

    def about_functional_load(self):
        about = AboutWindow('Functional load',
                    ('This function calculates the functional load of the contrast'
                    ' between any two segments, based on either the number of minimal'
                    ' pairs or the change in entropy resulting from merging that contrast.'),
                    ['Surendran, Dinoj & Partha Niyogi. 2003. Measuring the functional load of phonological contrasts. In Tech. Rep. No. TR-2003-12.',
                    'Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013. High functional load inhibits phonological contrast loss: A corpus study. Cognition 128.179-86'],
                    ['Blake Allen'])

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
                                    args=(self.corpus,[(s1, s2)]),
                                    kwargs={'frequency_cutoff':frequency_cutoff,
                                    'relative_count':relative_count,
                                    'distinguish_homophones':distinguish_homophones,
                                    'threaded_q':self.fl_q})
        else:
            functional_load_thread = ThreadedTask(self.fl_q,
                                    target=FL.deltah_fl,
                                    args=(self.corpus,[(s1, s2)]),
                                    kwargs={'frequency_cutoff':frequency_cutoff,
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
        self.fl_results = ResultsWindow(title,header)
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
        self.fl_results.update([self.fl_seg1_var.get(),
                                        self.fl_seg2_var.get(),
                                        fl_type,
                                        result,
                                        ignored_homophones,
                                        relative_count,
                                        self.fl_frequency_cutoff_var.get()])

    def cancel_functional_load(self):
        self.delete_fl_results_table()
        self.destroy()

