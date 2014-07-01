
import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton, 
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE)
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue
import corpustools.acousticsim.main as AS

from corpustools.gui.basegui import AboutWindow, FunctionWindow, ResultsWindow, MultiListbox, ThreadedTask

class ASAbout(AboutWindow):
    def __init__(self,master=None, **options):
        super(ASAbout, self).__init__(master=master, **options)
        self.title('Acoustic similarity')
        desc_frame = LabelFrame(self, text='Brief description')
        desc_label = Label(desc_frame, text='This function calculates the acoustic similarity of sound files in two directories by generating either MFCCs or amplitude envelopes for each sound file and using dynamic time warping or cross-correlation to get the average distance/similarity across all tokens.')
        desc_label.grid()
        desc_frame.grid(sticky=W)
        source_frame = LabelFrame(self, text='Original sources')

        source_label = Label(source_frame, text='Ellis, Daniel P. W. 2005. PLP and RASTA (and MFCC, and inversion) in Matlab (online web resource). http://www.ee.columbia.edu/~dpwe/resources/matlab/rastamat/.')
        source_label.grid()
        source_label2 = Label(source_frame, text='Lewandowski, Natalie. 2012. Talent in nonnative phonetic convergence. PhD Thesis.')
        source_label2.grid()
        source_frame.grid(sticky=W)
        coder_frame = LabelFrame(self, text='Coded by')
        coder_label = Label(coder_frame, text='Michael McAuliffe')
        coder_label.grid()
        coder_frame.grid(sticky=W)
    

class ASFunction(FunctionWindow):
    def __init__(self,master=None, **options):
        self.as_directory_one = StringVar()
        self.as_directory_two = StringVar()
        self.as_representation = StringVar()
        self.as_match_func = StringVar()
        self.as_num_filters = StringVar()
        self.as_num_coeffs = StringVar()
        self.as_min_freq = StringVar()
        self.as_max_freq = StringVar()
        self.as_output_sim = BooleanVar()
        self.as_use_multi = BooleanVar()
        self.as_q = queue.Queue()
        self.as_results_table = None
        super(ASFunction, self).__init__(master=master, **options)
        self.title('Acoustic similarity')
        dir_frame = LabelFrame(self,text='Directories')
        as_dir_one_label = Label(dir_frame, text='First directory')
        as_dir_one_label.grid(row=0, column=0)
        dir_one_text = Entry(dir_frame,textvariable=self.as_directory_one)
        dir_one_text.grid(row=0,column=1)
        def set_dir_one():
            dir_one = FileDialog.askdirectory()
            if dir_one:
                dir_one_text.delete(0,END)
                dir_one_text.insert(0, dir_one)

        find_dir_one = Button(dir_frame, text='Choose directory...', command=set_dir_one)
        find_dir_one.grid(row=0,column=2)

        as_dir_two_label = Label(dir_frame, text='Second directory')
        as_dir_two_label.grid(row=1, column=0)
        dir_two_text = Entry(dir_frame,textvariable=self.as_directory_two)
        dir_two_text.grid(row=1,column=1)
        def set_dir_two():
            dir_two = FileDialog.askdirectory()
            if dir_two:
                dir_two_text.delete(0,END)
                dir_two_text.insert(0, dir_two)

        find_dir_two = Button(dir_frame, text='Choose directory...', command=set_dir_two)
        find_dir_two.grid(row=1,column=2)

        dir_frame.grid()
        as_option_frame = LabelFrame(self,text='Parameters')
        representation_frame = LabelFrame(as_option_frame, text='Representation')
        mfcc = Radiobutton(representation_frame, text='MFCC',
                                    value='mfcc', variable=self.as_representation)
        mfcc.grid(sticky=W)
        mfcc.invoke()
        envelopes = Radiobutton(representation_frame, text='Amplitude envelopes',
                                    value='envelopes', variable=self.as_representation)
        envelopes.grid(sticky=W)
        representation_frame.grid(sticky=W)

        match_func_frame = LabelFrame(as_option_frame, text='Similarity algorithm')
        dtw = Radiobutton(match_func_frame, text='Dynamic time warping',
                                    value='dtw', variable=self.as_match_func)
        dtw.grid(sticky=W)
        dtw.invoke()
        xcorr = Radiobutton(match_func_frame, text='Cross-correlation',
                                    value='xcorr', variable=self.as_match_func)
        xcorr.grid(sticky=W)
        match_func_frame.grid(sticky=W)

        freq_frame = LabelFrame(as_option_frame, text='Frequency limits')
        as_min_freq_label = Label(freq_frame, text='Minimum frequency (Hz)')
        as_min_freq_label.grid(row=0, column=0)
        as_min_freq_entry = Entry(freq_frame, textvariable=self.as_min_freq)
        as_min_freq_entry.delete(0,END)
        as_min_freq_entry.insert(0,'80')
        as_min_freq_entry.grid(row=0, column=1)

        as_max_freq_label = Label(freq_frame, text='Maximum frequency (Hz)')
        as_max_freq_label.grid(row=1, column=0)
        as_max_freq_entry = Entry(freq_frame, textvariable=self.as_max_freq)
        as_max_freq_entry.delete(0,END)
        as_max_freq_entry.insert(0,'7800')
        as_max_freq_entry.grid(row=1, column=1)
        freq_frame.grid(sticky=W)

        freq_res_frame = LabelFrame(as_option_frame, text='Frequency resolution')
        as_num_filters_label = Label(freq_res_frame, text='Number of filters')
        as_num_filters_label.grid(row=0, column=0)
        as_num_filters_entry = Entry(freq_res_frame, textvariable=self.as_num_filters)
        as_num_filters_entry.delete(0,END)
        as_num_filters_entry.insert(0,'0')
        as_num_filters_entry.grid(row=0, column=1)

        as_num_coeffs_label = Label(freq_res_frame, text='Number of coefficents (MFCC only)')
        as_num_coeffs_label.grid(row=1, column=0)
        as_num_coeffs_entry = Entry(freq_res_frame, textvariable=self.as_num_coeffs)
        as_num_coeffs_entry.delete(0,END)
        as_num_coeffs_entry.insert(0,'0')
        as_num_coeffs_entry.grid(row=1, column=1)
        freq_res_frame.grid(sticky=W)

        output_frame = LabelFrame(as_option_frame, text='Output')
        sim = Radiobutton(output_frame, text='Output as similarity (0 to 1)',
                                    value=True, variable=self.as_output_sim)
        sim.grid(sticky=W)
        sim.invoke()
        dist = Radiobutton(output_frame, text='Output as distance',
                                    value=False, variable=self.as_output_sim)
        dist.grid(sticky=W)
        output_frame.grid(sticky=W)

        mp_frame = LabelFrame(as_option_frame, text='Multiprocessing')
        multi = Radiobutton(mp_frame, text='Use multiprocessing',
                                    value=True, variable=self.as_use_multi)
        multi.grid(sticky=W)
        multi.invoke()
        single = Radiobutton(mp_frame, text='Output as distance',
                                    value=False, variable=self.as_use_multi)
        single.grid(sticky=W)
        mp_frame.grid(sticky=W)

        as_option_frame.grid()

        button_frame = Frame(self)
        ok_button = Button(button_frame, text='Calculate acoustic similarity\n(start new results table)', command=lambda x=False: self.calculate_acoustic_similarity(update=x))
        ok_button.grid(row=0, column=0)
        self.update_as_button = Button(button_frame, text='Calculate acoustic similarity\n(add to current results table)', command=lambda x=True:self.calculate_acoustic_similarity(update=x))
        self.update_as_button.grid()
        self.update_as_button.config(state=DISABLED)
        cancel_button = Button(button_frame, text='Cancel', command=self.cancel_acoustic_similarity)
        cancel_button.grid(row=0, column=1)
        about = Button(button_frame, text='About this function...', command=self.about_acoustic_similarity)
        about.grid(row=0, column=2)
        button_frame.grid()
        
    def about_acoustic_similarity(self):
        about_as = ASAbout(master=self)
        
    def cancel_acoustic_similarity(self):
        self.destroy()
        
    def calculate_acoustic_similarity(self,update=False):
        d1 = self.as_directory_one.get()
        d2 = self.as_directory_two.get()
        if not d1 or not d2:
            MessageBox.showwarning(message='Please select two directories.')
            return
        if not os.path.exists(d1):
            MessageBox.showwarning(message='Directory \'%s\' does not exist.' % d1)
            return
        if not os.path.exists(d2):
            MessageBox.showwarning(message='Directory \'%s\' does not exist.' % d2)
            return
        if sum(os.path.isfile(os.path.join(d1, f)) for f in os.listdir(d1) if f.lower().endswith('.wav')) == 0:
            MessageBox.showwarning(message='Directory \'%s\' does not contain any sound files.' % d1)
            return
        if sum(os.path.isfile(os.path.join(d2, f)) for f in os.listdir(d2) if f.lower().endswith('.wav')) == 0:
            MessageBox.showwarning(message='Directory \'%s\' does not contain any sound files.' % d2)
            return
        if not update and self.as_results_table is not None:
            carryon = MessageBox.askyesno(message='You have acoustic similarity results open in a table already.\nWould you like to start a new table?')
            if not carryon:
                return
            else:
                self.as_results_table.destroy()
                self.as_results.destroy()
        rep = self.as_representation.get()
        match_func = self.as_match_func.get()
        min_freq = int(self.as_min_freq.get())
        max_freq = int(self.as_max_freq.get())
        num_coeffs = int(self.as_num_coeffs.get())
        if num_coeffs == 0 and rep == 'mfcc':
            num_coeffs = 12
            self.as_num_coeffs.set(str(num_coeffs))
        num_filters = int(self.as_num_filters.get())
        if num_filters == 0:
            if rep == 'mfcc':
                num_filters = 26
            elif rep == 'envelopes':
                num_filters = 8
            self.as_num_filters.set(str(num_filters))
        if num_coeffs >= num_filters:
            num_coeffs = num_filters - 1
            self.as_num_coeffs.set(str(num_coeffs))
        output_sim = self.as_output_sim.get()
        use_multi = self.as_use_multi.get()
        acoustic_similarity_thread = ThreadedTask(self.as_q,
                                    target=AS.acoustic_similarity_directories,
                                    args=(d1, d2),
                                    kwargs={'rep':rep,
                                    'match_function':match_func,
                                    'num_filters':num_filters,
                                    'num_coeffs': num_coeffs,
                                    'freq_lims': (min_freq,max_freq),
                                    'output_sim':output_sim,
                                    'use_multi':use_multi,
                                    'threaded_q':self.as_q})
        acoustic_similarity_thread.start()
        self.process_as_queue(update)


    def process_as_queue(self,update):
        try:
            result = self.as_q.get(0)
            if update:
                self.update_as_results(result) #results window exists, just return a new value
            else:
                self.show_as_result(result) #construct a new window to display results

        except queue.Empty:
            self.after(100, lambda x=update:self.process_as_queue(update))


    def show_as_result(self, result):
        header = [('Directory 1',10),
                ('Directory 2',10),
                ('Representation', 10),
                ('Match function', 10),
                ('Minimum frequency',5),
                ('Maximum frequency',5),
                ('Number of filters',5),
                ('Number of coefficients',5),
                ('Result',20),
                ('Is similarity?',5)]
        self.as_results = ResultsWindow('Acoustic similarity results',header)
        self.update_as_button.config(state=ACTIVE)
        self.update_as_results(result)

    def update_as_results(self, result):
        if self.as_representation.get() == 'mfcc':
            as_rep = 'MFCC'
        elif self.as_representation.get() == 'envelopes':
            as_rep = 'Amplitude envelopes'
        if self.as_match_func.get() == 'dtw':
            match_func = 'Dynamic time warping'
        elif self.as_match_func.get() == 'xcorr':
            match_func = 'Cross-correlation'
        try:
            self.as_results.update([os.path.split(self.as_directory_one.get())[1],
                                            os.path.split(self.as_directory_two.get())[1],
                                            as_rep,
                                            match_func,
                                            self.as_min_freq.get(),
                                            self.as_max_freq.get(),
                                            self.as_num_filters.get(),
                                            self.as_num_coeffs.get(),
                                            result,
                                            self.as_output_sim.get()])
        except TclError:
            self.show_as_result(result)
        
    

    
