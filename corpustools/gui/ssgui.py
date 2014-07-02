import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton, 
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE)
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue
import corpustools.symbolsim.string_similarity as SS

from corpustools.gui.basegui import AboutWindow, FunctionWindow, ResultsWindow, MultiListbox, ThreadedTask


class SSAbout(AboutWindow):
    def __init__(self,master=None, **options):
        super(SSAbout, self).__init__(master=master, **options)
        self.title('About the string similarity function')
        description_frame = LabelFrame(self, text='Brief description')
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
        citation_frame = LabelFrame(self, text='Original source')
        citation_label = Label(citation_frame, text='Khorsi, A. 2012. On Morphological Relatedness. Natural Language Engineering, 1-19.')
        citation_label.grid()
        citation_frame.grid(sticky=W)
        author_frame = LabelFrame(self, text='Coded by')
        author_label = Label(author_frame, text='Micheal Fry')
        author_label.grid()
        author_frame.grid(sticky=W)
    

class SSFunction(FunctionWindow):
    def __init__(self,master=None, **options):
        super(ASFunction, self).__init__(master=master, **options)
        
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
    
