import threading
import os
import sys
from tkinter import (Toplevel, Frame, Listbox, Scrollbar, END, BOTH, LEFT,
                    YES, X, FALSE, VERTICAL, Y, RAISED, FLAT, Label,
                    StringVar, LabelFrame,Label, Button, Entry, Canvas, W)
from tkinter import Radiobutton as OldRadiobutton
import tkinter.filedialog as FileDialog

from corpustools.config import DEFAULT_DATA_DIR, CONFIG_PATH, LOG_DIR, ERROR_DIR, config

class InventoryFrame(LabelFrame):

    def __init__(self, inventory, var, text, colmax=10, master=None):
        super(InventoryFrame, self).__init__(master=master, text=text)
        ipa_frame = LabelFrame(self, text='Sounds')
        seg1_frame = LabelFrame(ipa_frame, text=text)
        col = 0
        row = 0
        for seg in inventory:
            seg_button = OldRadiobutton(self, text=seg, variable=var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1

class PreferencesWindow(Toplevel):
    def __init__(self,master=None, **options):
        super(PreferencesWindow, self).__init__(master=master, **options)
        self.title('CorpusTools preferences')
        self.storage_directory = StringVar()
        dir_frame = LabelFrame(self,text='Directories')
        storage_dir_label = Label(dir_frame, text='Storage directory')
        storage_dir_label.grid(row=0, column=0)
        storage_dir_text = Entry(dir_frame,textvariable=self.storage_directory)
        storage_dir_text.delete(0,END)
        storage_dir_text.insert(0, config['storage']['directory'])
        storage_dir_text.grid(row=0,column=1)

        def set_dir():
            directory = FileDialog.askdirectory()
            if directory:
                storage_dir_text.delete(0,END)
                storage_dir_text.insert(0, directory)

        find_dir = Button(dir_frame, text='Choose directory...', command=set_dir)
        find_dir.grid(row=0,column=2)

        dir_frame.grid()

        button_frame = Frame(self)
        print_button = Button(button_frame, text='Ok', command=self.save_config)
        print_button.grid(row=0, column=0)
        close_button = Button(button_frame, text='Cancel', command=self.cancel_config)
        close_button.grid(row=0, column=1)
        button_frame.grid()

    def save_config(self):
        directory = self.storage_directory.get()
        if os.path.exists(directory):
            config['storage']['directory'] = directory

        with open(CONFIG_PATH,'w') as configfile:
            config.write(configfile)
        self.destroy()

    def cancel_config(self):
        self.destroy()


class AboutWindow(Toplevel):
    def __init__(self,title,description,sources,coders,wraplength=700):
        super(AboutWindow, self).__init__()
        self.title(title)
        desc_frame = LabelFrame(self, text='Brief description')
        desc_label = Label(desc_frame, text=description, wraplength=wraplength, justify=LEFT)
        desc_label.grid()
        desc_frame.grid(sticky=W)
        source_frame = LabelFrame(self, text='Original sources')
        for source in sources:
            source_label = Label(source_frame, text=source)
            source_label.grid(sticky=W)
        source_frame.grid(sticky=W)
        coder_frame = LabelFrame(self, text='Coded by')
        coder_label = Label(coder_frame, text=','.join(coders))
        coder_label.grid()
        coder_frame.grid(sticky=W)
        self.focus()

class FunctionWindow(Toplevel):
    pass


class ResultsWindow(Toplevel):
    def __init__(self, title, headerline, master=None, delete_method=None, **options):
        super(ResultsWindow, self).__init__(master=master, **options)

        self.title(title)

        self.as_results_table = MultiListbox(self,headerline)
        self.as_results_table.grid()

        self.delete_results = delete_method

        button_frame = Frame(self)
        print_button = Button(button_frame, text='Save results to file', command=self.save_results)
        print_button.grid(row=0, column=0)
        close_button = Button(button_frame, text='Close this table', command=self.delete_results)
        close_button.grid(row=0, column=1)
        button_frame.grid()


    def delete_results(self):
        pass #see self.__init__()

    def save_results(self):
        filename = FileDialog.asksaveasfilename()
        if not filename.endswith('.txt'):
            filename += '.txt'
        with open(filename, mode='w', encoding='utf-8') as f:
            print('\t'.join([h for h in self.as_results_table.headers]), file=f)
            for result in zip(*self.as_results_table.get(0)):
                print('\t'.join(str(r) for r in result)+'\r\n', file=f)

    def update(self, resultline):
        self.as_results_table.insert(END,resultline)


class ThreadedTask(threading.Thread):
    def __init__(self, queue, target, args, **kwargs):
        if kwargs:
            threading.Thread.__init__(self,target=target, args=args, kwargs=kwargs['kwargs'])
        else:
            threading.Thread.__init__(self,target=target, args=args)
        self.queue = queue

class MultiListbox(Frame):
    def __init__(self, master, lists):
        Frame.__init__(self, master)
        self.lists = []
        self.headers = [l for l,w in lists]
        for l,w in lists:
            frame = Frame(self); frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0,relief=FLAT, exportselection=FALSE)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
        frame = Frame(self); frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(expand=YES, fill=Y)
        self.lists[0]['yscrollcommand']=sb.set

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        return 'break'

    def _button2(self, x, y):
        for l in self.lists:
            l.scan_mark(x, y)
        return 'break'

    def _b2motion(self, x, y):
        for l in self.lists:
            l.scan_dragto(x, y)
        return 'break'

    def _scroll(self, *args):
        for l in self.lists:
            l.yview(*args)

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=END):
        result = []
        for l in self.lists:
            result.append(l.get(first,last))

        return result

##    def __len__(self):
##        return self.size()

    def index(self, index):
        self.lists[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)

class ToolTip:
    """
    Michael Lange <klappnase (at) freakmail (dot) de>
    The ToolTip class provides a flexible tooltip widget for Tkinter; it is based on IDLE's ToolTip
    module which unfortunately seems to be broken (at least the version I saw).
    INITIALIZATION OPTIONS:
    anchor :        where the text should be positioned inside the widget, must be on of "n", "s", "e", "w", "nw" and so on;
                    default is "center"
    bd :            borderwidth of the widget; default is 1 (NOTE: don't use "borderwidth" here)
    bg :            background color to use for the widget; default is "lightyellow" (NOTE: don't use "background")
    delay :         time in ms that it takes for the widget to appear on the screen when the mouse pointer has
                    entered the parent widget; default is 1500
    fg :            foreground (i.e. text) color to use; default is "black" (NOTE: don't use "foreground")
    follow_mouse :  if set to 1 the tooltip will follow the mouse pointer instead of being displayed
                    outside of the parent widget; this may be useful if you want to use tooltips for
                    large widgets like listboxes or canvases; default is 0
    font :          font to use for the widget; default is system specific
    justify :       how multiple lines of text will be aligned, must be "left", "right" or "center"; default is "left"
    padx :          extra space added to the left and right within the widget; default is 4
    pady :          extra space above and below the text; default is 2
    relief :        one of "flat", "ridge", "groove", "raised", "sunken" or "solid"; default is "solid"
    state :         must be "normal" or "disabled"; if set to "disabled" the tooltip will not appear; default is "normal"
    text :          the text that is displayed inside the widget
    textvariable :  if set to an instance of Tkinter.StringVar() the variable's value will be used as text for the widget
    width :         width of the widget; the default is 0, which means that "wraplength" will be used to limit the widgets width
    wraplength :    limits the number of characters in each line; default is 150

    WIDGET METHODS:
    configure(**opts) : change one or more of the widget's options as described above; the changes will take effect the
                        next time the tooltip shows up; NOTE: follow_mouse cannot be changed after widget initialization

    Other widget methods that might be useful if you want to subclass ToolTip:
    enter() :           callback when the mouse pointer enters the parent widget
    leave() :           called when the mouse pointer leaves the parent widget
    motion() :          is called when the mouse pointer moves inside the parent widget if follow_mouse is set to 1 and the
                        tooltip has shown up to continually update the coordinates of the tooltip window
    coords() :          calculates the screen coordinates of the tooltip window
    create_contents() : creates the contents of the tooltip window (by default a Tkinter.Label)
    """
    def __init__(self, master, text='Your text here', delay=1500, **opts):
        self.master = master
        self._opts = {'anchor':'center', 'delay':delay,
                      'follow_mouse':0, 'font':None, 'justify':'left',
                      'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,
                      'width':0, 'wraplength':300}
                      #the following options didn't play nice with ttk
                      #and had to be removed
                      #fg, bg, padx, pady, bd
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1

    def configure(self, **opts):
        for key in opts:
            value = opts.get(key)
            if value is not None:
                self._opts[key] = value
            else:
                raise KeyError('{} is not an option for ToolTip'.format(str(value)))

    ##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
    ##----events on the parent widget; override them if you want to change the widget's behavior--##

    def enter(self, event=None):
        self._schedule()

    def leave(self, event=None):
        self._unschedule()
        self._hide()

    def motion(self, event=None):
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))

    ##------the methods that do the work:---------------------------------------------------------##

    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()

    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()

    ##----these methods might be overridden in derived classes:----------------------------------##

    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = Label(self._tipwindow, **opts)
        label.pack()

class TableView(Frame):
    def __init__(self, root):

        Frame.__init__(self, root)
        self.headerframe = Frame(self)
        self.headerframe.pack(side='top',fill='x')
        self.set_header(['spelling','transcription','frequency'])
        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = Frame(self.canvas, background="#ffffff")
        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        #self.frame.bind("<Configure>", self.OnFrameConfigure)

        #self.populate()

    def set_header(self,header):
        for child in self.headerframe.winfo_children():
            child.grid_forget()
        for i,h in enumerate(header):
            Label(self.headerframe, text=h).grid(row=0, column=i)

    def load_corpus(self,corpus):
        ''''''
        for child in self.frame.winfo_children():
            child.grid_forget()
        if corpus is None:
            return
        print(self.frame.grid_size())
        random_word = corpus.random_word()
        headers = [d for d in random_word.descriptors if not d is None or not d == '']
        self.set_header(headers)
        for i,word in enumerate(corpus.iter_sort()):
            #corpus.iter_sort is a generator that sorts the corpus dictionary
            #by keys, then yields the values in that order
            for j,d in enumerate(word.descriptors):
                Label(self.frame, text="%s" % str(getattr(word,d,'???'))).grid(row=i, column=j)


    def OnFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
