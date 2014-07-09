import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE)
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue

from corpustools.gui.basegui import (AboutWindow, FunctionWindow,
                    ResultsWindow, InventoryFrame, MultiListbox, ThreadedTask, ToolTip)

class FAFunction(FunctionWindow):

    def __init__(self,master,corpus):

        self.seg1_var = StringVar()
        self.seg2_var = StringVar()
        self.corpus = corpus

        super(FAFunction, self).__init__(master=master)
        inv_frame = LabelFrame(self, text='Select two sounds')
        seg1_frame = InventoryFrame(self.corpus.get_inventory(), self.seg1_var, 'Sound 1')
        seg2_frame = InventoryFrame(self.corpus.get_inventory(), self.seg2_var, 'Sound 2')
        inv_frame.grid()


