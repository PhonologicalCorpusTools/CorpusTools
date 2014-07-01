import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton, 
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE)
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue

from corpustools.gui.basegui import AboutWindow, FunctionWindow, ResultsWindow, MultiListbox, ThreadedTask


class PDAbout(AboutWindow):
    pass
    

class PDFunction(FunctionWindow):
    pass
    
