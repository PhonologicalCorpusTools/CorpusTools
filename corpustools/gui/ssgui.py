import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE, Listbox, N)

import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue
import corpustools.symbolsim.string_similarity as SS

from corpustools.gui.basegui import (AboutWindow, FunctionWindow, 
                                    ResultsWindow, ThreadedTask, ToolTip)

class SSFunction(FunctionWindow):
    def __init__(self,corpus,master=None, **options):
        super(SSFunction, self).__init__(master=master, **options)
        self.corpus = corpus
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
        self.title('String similarity')

        relator_type_frame = LabelFrame(self, text='String similarity algorithm')
        self.relator_selection = Listbox(relator_type_frame)
        for rtype in ['Khorsi', 'Edit distance', 'Phonological edit distance']:
            self.relator_selection.insert(0, rtype)
        self.relator_selection.grid()
        relator_type_frame.grid(row=0,column=0,sticky=N)

        comparison_type_frame = LabelFrame(self, text='Comparison type')
        word1_frame = Frame(comparison_type_frame)
        one_word_radiobutton = Radiobutton(word1_frame, text='Compare one word to entire corpus',
                                    variable=self.string_similarity_comparison_type_var, value='one')
        one_word_radiobutton.grid(sticky=W)
        one_word_radiobutton.invoke()
        word1_frame.grid(sticky=W)
        word1_entry = Entry(word1_frame, textvariable=self.string_similarity_query_var)
        #word1_entry.delete(0,END)
        #word1_entry.insert(0,selection)
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

        def get_word_pairs_file():
            filename = FileDialog.askopenfilename()

            if not filename:
                return
            if not filename.endswith('.txt'):
                filename += '.txt'
            self.string_similarity_pairs_var.set(filename)

        get_word_pairs_button = Button(word_pairs_frame, text='Choose word pairs file', command=get_word_pairs_file)
        get_word_pairs_button.grid(sticky=W)
        get_word_pairs_label = Label(word_pairs_frame, textvariable=self.string_similarity_pairs_var)
        get_word_pairs_label.grid(sticky=W)
        word_pairs_frame.grid(sticky=W)


        comparison_type_frame.grid(row=0,column=1,sticky=N)

        options_frame = LabelFrame(self, text='Options')
        typetoken_frame = LabelFrame(options_frame, text='Type or Token')
        type_button = Radiobutton(typetoken_frame, text='Count types', variable=self.string_similarity_typetoken_var, value='type')
        type_button.grid(sticky=W)
        type_button.invoke()
        token_button = Radiobutton(typetoken_frame, text='Count tokens', variable=self.string_similarity_typetoken_var, value='token')
        token_button.grid(sticky=W)
        if self.corpus.custom and not self.corpus.has_frequency():
            token_button.configure(state=('disabled'))
        typetoken_frame.grid(column=0, row=0, sticky=W)
        stringtype_frame = LabelFrame(options_frame, text='String type')
        spelling_button = Radiobutton(stringtype_frame, text='Compare spelling', variable=self.string_similarity_stringtype_var, value='spelling')
        spelling_button.grid(sticky=W)
        spelling_button.invoke()
        if self.corpus.custom and not self.corpus.has_spelling():
            transcription_button.configure(state=('disabled'))
        transcription_button = Radiobutton(stringtype_frame, text='Compare transcription', variable=self.string_similarity_stringtype_var, value='transcription')
        transcription_button.grid(sticky=W)
        if self.corpus.custom and not self.corpus.has_transcription():
            transcription_button.configure(state=('disabled'))
        stringtype_frame.grid(column=0, row=1, sticky=W)
        threshold_frame = LabelFrame(options_frame, text='Return only results between...')
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

        button_frame = Frame(self)
        ok_button = Button(button_frame, text='OK', command=self.calculate_string_similarity)
        ok_button.grid(row=0,column=0)
        if self.corpus.custom and not self.corpus.has_spelling() and self.corpus.has_transcription():
            ok_button.state = DISABLED
        cancel_button = Button(button_frame, text='Cancel', command=self.cancel_string_similarity)
        cancel_button.grid(row=0, column=1)
        info_button = Button(button_frame, text='About this function...', command=self.about_string_similarity)
        info_button.grid(row=0,column=2)
        button_frame.grid(row=1)

        self.focus()

    def about_string_similarity(self):
        about = AboutWindow('About the string similarity function',
                ('This function calculates the similarity between words in the corpus,'
                ' based on either their spelling or their transcription. Similarity '
                'is a function of the longest common shared sequences of graphemes '
                'or phonemes (weighted by their frequency of occurrence in the corpus), '
                'subtracting out the non-shared graphemes or phonemes. The spelling '
                'version was originally proposed as a measure of morphological relatedness,'
                ' but is more accurately described as simply a measure of string similarity.'),
                ['Khorsi, A. 2012. On Morphological Relatedness. Natural Language Engineering, 1-19.'],
                ['Micheal Fry'])

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
                return
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
                message = 'The word \"{}\" is not in the corpus'.format(query1)
                MessageBox.showerror(message=message)
                return

            try:
                self.corpus.find(query2,keyerror=True)
            except KeyError:
                message = 'The word \"{}\" is not in the corpus'.format(query2)
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



        header = [('Word 1',20),
                    ('Word 2', 20),
                    ('Result', 10),
                    ('Type or token', 10),
                    ('Algorithm type', 10)]
        title = 'String similarity results'
        if self.string_similarity_comparison_type_var.get() == 'one':
            query = self.string_similarity_query_var.get()
            results = SS.string_similarity_word('',relator_type,
                                                string_type, typetoken, query,
                                                min_rel, max_rel, self.corpus, output_filename='return_data')
            results = [(query,x[1],x[0]) for x in results]
        elif self.string_similarity_comparison_type_var.get() == 'pairs':
            query = self.string_similarity_pairs_var.get()
            results = SS.string_similarity_pairs('', relator_type,
                                                    string_type, typetoken, query,
                                                    'return_data', min_rel, max_rel, self.corpus)

        elif self.string_similarity_comparison_type_var.get() == 'one_pair':
            word1 = self.string_similarity_one_pair1_var.get()
            word2 = self.string_similarity_one_pair2_var.get()
            results = [SS.string_similarity_single_pair('', relator_type, string_type, typetoken, word1, word2, self.corpus)]

        self.ss_results = ResultsWindow(title,header)

        for result in results:
            w1, w2, similarity = result
            if relator_type != 'khorsi':
                typetoken = 'N/A'
            self.ss_results.update([w1, w2, similarity, typetoken, relator_type])


    def cancel_string_similarity(self):
        self.destroy()

