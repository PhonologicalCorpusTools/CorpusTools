
import os

from tkinter import Tk
from corpustools.gui.maingui import GUI, make_menus,use_logo


root = Tk()
root.title("CorpusTools v0.15")
#logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.ico')
logo_path = 'logo.ico'
if use_logo:
    try:
        root.wm_iconbitmap(logo_path)
    except FileNotFoundError:
        pass#if the file isn't found, don't bother
    except:
        pass
app = GUI(root,os.path.dirname(logo_path))
make_menus(root,app)
root.bind_all('<Control-q>', app.quit)
root.mainloop()
