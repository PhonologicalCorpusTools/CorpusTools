
import os

from tkinter import Tk
from corpustools.gui.maingui import GUI, make_menus,use_logo

def main():
    root = Tk()
    root.title("CorpusTools v0.15")
    if use_logo:
        try:
            root.wm_iconbitmap(os.path.join(os.getcwd(),'sample_logo.ico'))
        except FileNotFoundError:
            pass#if the file isn't found, don't bother
    if not os.path.exists(os.path.join(os.getcwd(),'ERRORS')):
        os.mkdir(os.path.join(os.getcwd(),'ERRORS'))
    app = GUI(root)
    make_menus(root,app)
    root.bind_all('<Control-q>', app.quit)
    root.bind_all('<Control-h>', app.entropy)
    root.mainloop()
