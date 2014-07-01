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
    pass
    

class SSFunction(FunctionWindow):
    pass
    
