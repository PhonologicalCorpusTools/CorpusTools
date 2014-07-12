
import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE)
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue
import corpustools.acousticsim.main as AS

from corpustools.gui.basegui import (AboutWindow, FunctionWindow, 
                                    ResultsWindow, ThreadedTask, ToolTip)


class ASFunction(FunctionWindow):
    def __init__(self,master=None, **options):
        super(ASFunction, self).__init__(master=master, **options)

        self.directory_one = StringVar()
        self.directory_two = StringVar()
        self.representation = StringVar()
        self.match_func = StringVar()
        self.num_filters = StringVar()
        self.num_coeffs = StringVar()
        self.min_freq = StringVar()
        self.max_freq = StringVar()
        self.output_sim = BooleanVar()
        self.use_multi = BooleanVar()
        self.q = queue.Queue()
        self.results = None
        self.title('Acoustic similarity')
        dir_frame = LabelFrame(self,text='Directories')
        if self.show_tooltips:
            dir_frame_tooltip = ToolTip(dir_frame, follow_mouse=False,
                                    text='Choose two directories to compare sound files between.')

        
        dir_one_label = Label(dir_frame, text='First directory')
        dir_one_label.grid(row=0, column=0)
        dir_one_text = Entry(dir_frame,textvariable=self.directory_one)
        dir_one_text.grid(row=0,column=1)
        def set_dir_one():
            dir_one = FileDialog.askdirectory()
            if dir_one:
                dir_one_text.delete(0,END)
                dir_one_text.insert(0, dir_one)

        find_dir_one = Button(dir_frame, text='Choose directory...', command=set_dir_one)
        find_dir_one.grid(row=0,column=2)

        dir_two_label = Label(dir_frame, text='Second directory')
        dir_two_label.grid(row=1, column=0)
        dir_two_text = Entry(dir_frame,textvariable=self.directory_two)
        dir_two_text.grid(row=1,column=1)
        def set_dir_two():
            dir_two = FileDialog.askdirectory()
            if dir_two:
                dir_two_text.delete(0,END)
                dir_two_text.insert(0, dir_two)

        find_dir_two = Button(dir_frame, text='Choose directory...', command=set_dir_two)
        find_dir_two.grid(row=1,column=2)

        dir_frame.grid()
        option_frame = LabelFrame(self,text='Parameters')
        representation_frame = LabelFrame(option_frame, text='Representation')
        if self.show_tooltips:
            representation_frame_tooltip = ToolTip(representation_frame, follow_mouse=False,
                                    text='Choose how to represent acoustic waveforms.')

        mfcc = Radiobutton(representation_frame, text='MFCC',
                                    value='mfcc', variable=self.representation)
        mfcc.grid(sticky=W)
        mfcc.invoke()
        envelopes = Radiobutton(representation_frame, text='Amplitude envelopes',
                                    value='envelopes', variable=self.representation)
        envelopes.grid(sticky=W)
        representation_frame.grid(sticky=W)

        match_func_frame = LabelFrame(option_frame, text='Similarity algorithm')
        if self.show_tooltips:
            match_frame_tooltip = ToolTip(match_func_frame, follow_mouse=False,
                                    text='Choose how to compare representations.')
        dtw = Radiobutton(match_func_frame, text='Dynamic time warping',
                                    value='dtw', variable=self.match_func)
        dtw.grid(sticky=W)
        dtw.invoke()
        xcorr = Radiobutton(match_func_frame, text='Cross-correlation',
                                    value='xcorr', variable=self.match_func)
        xcorr.grid(sticky=W)
        match_func_frame.grid(sticky=W)

        freq_frame = LabelFrame(option_frame, text='Frequency limits')
        if self.show_tooltips:
            freq_frame_tooltip = ToolTip(freq_frame, follow_mouse=False,
                                    text='Choose frequency range.')
        min_freq_label = Label(freq_frame, text='Minimum frequency (Hz)')
        min_freq_label.grid(row=0, column=0)
        min_freq_entry = Entry(freq_frame, textvariable=self.min_freq)
        min_freq_entry.delete(0,END)
        min_freq_entry.insert(0,'80')
        min_freq_entry.grid(row=0, column=1)

        max_freq_label = Label(freq_frame, text='Maximum frequency (Hz)')
        max_freq_label.grid(row=1, column=0)
        max_freq_entry = Entry(freq_frame, textvariable=self.max_freq)
        max_freq_entry.delete(0,END)
        max_freq_entry.insert(0,'7800')
        max_freq_entry.grid(row=1, column=1)
        freq_frame.grid(sticky=W)

        freq_res_frame = LabelFrame(option_frame, text='Frequency resolution')
        if self.show_tooltips:
            freq_res_frame_tooltip = ToolTip(freq_res_frame, follow_mouse=False,
                                    text=('Choose how many filters to divide the frequency range'
                                            ' and how many coefficients to use for MFCC generation.'
                                            ' Leave as \'0\' for reasonable defaults based on the'
                                            ' representation.'))
        num_filters_label = Label(freq_res_frame, text='Number of filters')
        num_filters_label.grid(row=0, column=0)
        num_filters_entry = Entry(freq_res_frame, textvariable=self.num_filters)
        num_filters_entry.delete(0,END)
        num_filters_entry.insert(0,'0')
        num_filters_entry.grid(row=0, column=1)

        num_coeffs_label = Label(freq_res_frame, text='Number of coefficents (MFCC only)')
        num_coeffs_label.grid(row=1, column=0)
        num_coeffs_entry = Entry(freq_res_frame, textvariable=self.num_coeffs)
        num_coeffs_entry.delete(0,END)
        num_coeffs_entry.insert(0,'0')
        num_coeffs_entry.grid(row=1, column=1)
        freq_res_frame.grid(sticky=W)

        output_frame = LabelFrame(option_frame, text='Output')
        if self.show_tooltips:
            output_frame_tooltip = ToolTip(output_frame, follow_mouse=False,
                                    text=('Choose whether the result should be similarity'
                                            ' or distance. Similarity is inverse distance,'
                                            ' and distance is inverse similarity'))
        sim = Radiobutton(output_frame, text='Output as similarity (0 to 1)',
                                    value=True, variable=self.output_sim)
        sim.grid(sticky=W)
        sim.invoke()
        dist = Radiobutton(output_frame, text='Output as distance',
                                    value=False, variable=self.output_sim)
        dist.grid(sticky=W)
        output_frame.grid(sticky=W)

        mp_frame = LabelFrame(option_frame, text='Multiprocessing')
        if self.show_tooltips:
            mp_frame_tooltip = ToolTip(mp_frame, follow_mouse=False,
                                    text=('Choose whether to use multiple processes.'
                                            ' Multiprocessing is currently not supported'))
        multi = Radiobutton(mp_frame, text='Use multiprocessing',
                                    value=True, variable=self.use_multi)
        multi.grid(sticky=W)
        multi.invoke()
        single = Radiobutton(mp_frame, text='Use single processor',
                                    value=False, variable=self.use_multi)
        single.grid(sticky=W)
        mp_frame.grid(sticky=W)

        option_frame.grid()

        button_frame = Frame(self)
        ok_button = Button(button_frame, text='Calculate acoustic similarity\n(start new results table)', command=lambda x=False: self.calculate_acoustic_similarity(update=x))
        ok_button.grid(row=0, column=0)
        self.update_button = Button(button_frame, text='Calculate acoustic similarity\n(add to current results table)', command=lambda x=True:self.calculate_acoustic_similarity(update=x))
        self.update_button.grid()
        self.update_button.config(state=DISABLED)
        cancel_button = Button(button_frame, text='Cancel', command=self.cancel_acoustic_similarity)
        cancel_button.grid(row=0, column=1)
        about = Button(button_frame, text='About this function...', command=self.about_acoustic_similarity)
        about.grid(row=0, column=2)
        button_frame.grid()
        self.focus()

    def about_acoustic_similarity(self):
        about = AboutWindow('Acoustic similarity',
                ('This function calculates the acoustic similarity of sound files in two'
                ' directories by generating either MFCCs or amplitude envelopes for each'
                ' sound file and using dynamic time warping or cross-correlation to get '
                'the average distance/similarity across all tokens.'),
                ['Ellis, Daniel P. W. 2005. PLP and RASTA (and MFCC, and inversion) in Matlab (online web resource). http://www.ee.columbia.edu/~dpwe/resources/matlab/rastamat/.',
                'Lewandowski, Natalie. 2012. Talent in nonnative phonetic convergence. PhD Thesis.'],
                ['Michael McAuliffe'])

    def delete_results(self):

        #clean-up function
        if self.results is not None:
            self.results.destroy()
            self.results = None
            self.update_button.config(state=DISABLED)

    def cancel_acoustic_similarity(self):
        self.delete_results()
        self.destroy()

    def calculate_acoustic_similarity(self,update=False):
        d1 = self.directory_one.get()
        d2 = self.directory_two.get()
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
        if not update and self.results is not None:
            carryon = MessageBox.askyesno(message='You have acoustic similarity results open in a table already.\nWould you like to start a new table?')
            if not carryon:
                return
            else:
                self.results.destroy()
        rep = self.representation.get()
        match_func = self.match_func.get()
        min_freq = int(self.min_freq.get())
        max_freq = int(self.max_freq.get())
        num_coeffs = int(self.num_coeffs.get())
        if num_coeffs == 0 and rep == 'mfcc':
            num_coeffs = 12
            self.num_coeffs.set(str(num_coeffs))
        num_filters = int(self.num_filters.get())
        if num_filters == 0:
            if rep == 'mfcc':
                num_filters = 26
            elif rep == 'envelopes':
                num_filters = 8
            self.num_filters.set(str(num_filters))
        if num_coeffs >= num_filters:
            num_coeffs = num_filters - 1
            self.num_coeffs.set(str(num_coeffs))
        output_sim = self.output_sim.get()
        use_multi = self.use_multi.get()
        acoustic_similarity_thread = ThreadedTask(self.q,
                                    target=AS.acoustic_similarity_directories,
                                    args=(d1, d2),
                                    kwargs={'rep':rep,
                                    'match_function':match_func,
                                    'num_filters':num_filters,
                                    'num_coeffs': num_coeffs,
                                    'freq_lims': (min_freq,max_freq),
                                    'output_sim':output_sim,
                                    'use_multi':use_multi,
                                    'threaded_q':self.q})
        acoustic_similarity_thread.start()
        self.process_queue(update)


    def process_queue(self,update):
        try:
            result = self.q.get(0)
            if update:
                self.update_results(result) #results window exists, just return a new value
            else:
                self.show_result(result) #construct a new window to display results

        except queue.Empty:
            self.after(100, lambda x=update:self.process_queue(update))


    def show_result(self, result):
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
        self.results = ResultsWindow('Acoustic similarity results',header,delete_method=self.delete_results)
        self.update_button.config(state=ACTIVE)
        self.update_results(result)

    def update_results(self, result):
        if self.representation.get() == 'mfcc':
            rep = 'MFCC'
        elif self.representation.get() == 'envelopes':
            rep = 'Amplitude envelopes'
        if self.match_func.get() == 'dtw':
            match_func = 'Dynamic time warping'
        elif self.match_func.get() == 'xcorr':
            match_func = 'Cross-correlation'
        try:
            self.results.update([os.path.split(self.directory_one.get())[1],
                                            os.path.split(self.directory_two.get())[1],
                                            rep,
                                            match_func,
                                            self.min_freq.get(),
                                            self.max_freq.get(),
                                            self.num_filters.get(),
                                            self.num_coeffs.get(),
                                            result,
                                            self.output_sim.get()])
        except TclError:
            self.show_result(result)




