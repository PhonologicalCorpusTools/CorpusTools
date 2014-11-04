import threading
import os
import operator
import sys
from tkinter import (Toplevel, Frame, Listbox, Scrollbar, END, BOTH, LEFT,
                    YES, X, FALSE, VERTICAL, Y, SUNKEN, RAISED, FLAT, Label,
                    StringVar, LabelFrame,Label, Button, Entry, Canvas, W, N)
from tkinter import Radiobutton as OldRadiobutton
import tkinter.filedialog as FileDialog

from corpustools.config import DEFAULT_DATA_DIR, CONFIG_PATH, LOG_DIR, ERROR_DIR, config


class InventoryFrame(LabelFrame):

    def __init__(self, corpus, var, title, master=None):
        super().__init__(master=master)
        self.corpus = corpus
        self.seg_var = var
        self.configure(text=title)
        self.buttons = list()
        self.Cinventory_frame = LabelFrame(self)
        self.Vinventory_frame = LabelFrame(self)
        self.Cinventory_frame.grid(row=0,column=0,sticky=N, padx=5)
        self.Vinventory_frame.grid(row=0,column=1,sticky=N, padx=5)


    def show(self, hide=None):
        """
        Put the inventory on screen, making each segment a button that pops up
        a window to view more detailed segmental information.

        Arguments
        ---------
        hide    Can be 'C', 'V', or None. The strings hide either vowels or consonants
                from being displayed. If hide is None, both are displayed.
        """

        if hide == 'V':
            self.chosen_chart = ConsChart(self.Cinventory_frame)
            self.populate_chart()
            self.chosen_chart.grid()
        elif hide == 'C':
            self.chosen_chart = VowelChart(self.Vinventory_frame)
            self.populate_chart()
            self.chosen_chart.grid()
        elif hide is None:
            self.chosen_chart = ConsChart(self.Cinventory_frame)
            self.populate_chart()
            self.chosen_chart.grid()
            self.chosen_chart = VowelChart(self.Vinventory_frame)
            self.populate_chart()
            self.chosen_chart.grid()

    def populate_chart(self):

        for seg in self.corpus.inventory:
            if seg == '#':
                continue
            features = self.corpus.segment_to_features(seg)
            if ((isinstance(self.chosen_chart, VowelChart) and (features['voc']=='+'))
                or
                (isinstance(self.chosen_chart, ConsChart) and (features['voc']=='-'))):

                self.chosen_chart.match_to_chart(seg,features)

        if isinstance(self.chosen_chart, ConsChart):
            word = 'Consonant'
        else:
            word = 'Vowel'

        self.chosen_chart.master.config(text='{} inventory'.format(word))

        row = 1
        col = 2

        for cname in self.chosen_chart.col_names:
            col_label = Label(self.chosen_chart.master, text=cname)
            col_label.grid(row=1, column=col)
            col += 1

        for rname in self.chosen_chart.row_names:
            row += 1
            col = 1
            row_label = Label(self.chosen_chart.master, text=rname)
            row_label.grid(row=row, column=col)
            for cname in self.chosen_chart.col_names:
                col += 1
                seg_box = Frame(self.chosen_chart.master, borderwidth=10)
                seg_row = 0
                seg_col = 0
                seg_col_max = 4
                seg_list = sorted(self.chosen_chart.display_matrix[rname][cname], key=lambda x: x[1]==False)

                for seg,voiced in seg_list:
                    seg_button = Button(seg_box, text=seg, background='grey')
                    seg_button.bind('<Button-1>', self.select_seg)
                    self.buttons.append(seg_button)
                    seg_button.grid(row=seg_row, column=seg_col)
                    seg_col += 1
                    if seg_col == seg_col_max:
                        seg_col = 0
                        seg_row += 1
                seg_box.grid(row=row,column=col)
        row+=1
        col=1
        row_label = Label(self.chosen_chart.master, text='Uncategorized')
        row_label.grid(row=row, column=col)
        nomatch_box = Frame(self.chosen_chart.master, borderwidth=10)
        for seg,marked in self.chosen_chart.display_matrix['nomatch']:
            col+=1
            seg_box.grid(row=row, column=col)
            seg_button = Button(nomatch_box, text=seg, background='grey')
            seg_button.bind('<Button-1>', self.select_seg)
            self.buttons.append(seg_button)
            seg_button.grid()

    def select_seg(self, event=None):
        button = event.widget
        seg_symbol = button.config('text')[-1]
        self.seg_var.set(seg_symbol)
        for b in self.buttons:
            b.config(background='grey')
        button.config(background='gold')


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
        config['storage']['directory'] = directory

        with open(CONFIG_PATH,'w') as configfile:
            config.write(configfile)
        corpus_path = os.path.join(directory,'CORPUS')
        if not os.path.exists(corpus_path):
            os.makedirs(corpus_path)
        trans_path = os.path.join(directory,'TRANS')
        if not os.path.exists(trans_path):
            os.makedirs(trans_path)
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
    def __init__(self, master=None, **options):
        if 'show_tooltips' in options:
            self.show_tooltips = options.get('show_tooltips')
            del options['show_tooltips']
        super(FunctionWindow, self).__init__(master=master, **options)


class IPAChart():
    """
    Base class for Consonant and Vowel charts. Includes methods for matching
    a Segment to a chart
    """

    def match_to_chart(self,input_seg,input_features):
        """
        Takes a Segment as input an places it in the appropriate row
        and column in a Chart
        """

        #the original code this comes from assumed a list as input, so I convert
        #to one here. I also erase any 'n' values for the moment and treat them
        #as '-' values.
        input_features = [v+k if not v=='n' else '-'+k for (k,v) in input_features.items()]

        #segments can be coloured in on a chart to show an additional feature
        #value. right now voiced consonants are coloured in, and voiceless one
        #are not and rounded vowels are coloured in while unrounced vowels
        #are not
        if ('-voc' in input_features) and ('+voice' in input_features):
            marked = True
        elif ('+voc' in input_features) and ('+round' in input_features):
            marked = True
        else:
            marked = False

        rmatch = False
        cmatch = False
        for rname,rfeatures in self.row_descriptions:
            if all([feature in input_features for feature in rfeatures.split(',')]):
                rmatch = rname
                break

        for cname,cfeatures in self.col_descriptions:
            if all([feature in input_features for feature in cfeatures.split(',')]):
                cmatch = cname
                break

        if not rmatch or not cmatch:
            self.display_matrix['nomatch'].append((input_seg, marked))
        else:
            self.display_matrix[rmatch][cmatch].append((input_seg, marked))


class VowelChart(Frame, IPAChart):

    def __init__(self, master):
        super(VowelChart,self).__init__(master)
        self.row_descriptions = [('high','-low,+high'),
                                ('low mid','-low,-high'),
                                ('high mid','+low,+high'),
                                ('low','+low,-high')]
        self.row_names = [height for height,description in self.row_descriptions]
        self.col_descriptions = [('front','-back'),
                                ('mid','nback'),
                                ('back','+back')]
        self.col_names = [back for back,description in self.col_descriptions]
        self.display_matrix = {rname:{cname:list() for cname in self.col_names} for rname in self.row_names}
        self.display_matrix['nomatch'] = list()

class ConsChart(Frame, IPAChart):
    """
    Frame for displaying only consonants. Roughly divided up using IPA-style
    articulatory features, e.g. "labial", "dental", "palatal", etc. and
    same for manners "stop", "nasal", "fricative", etc.
    """

    def __init__(self, master):
        super(ConsChart,self).__init__(master)
        self.row_descriptions = [('stop','-cont,-nasal,-son,-voc'),
                            ('nasal','+nasal,+son,-voc'),
                            ('-son nasal','+nasal,-son,-voc'),
                            ('fricative','+cont,-son,-nasal,-voc'),
                            ('lateral','+lat,-nasal,+son,-voc'),
                            ('approximant','+son,-nasal,-voc')]
        self.col_descriptions = [('labial','+ant,-cor,-back'),
                            ('dental','+cor,+ant,-back'),
                            ('coronal','+cor,-ant,-back'),
                            ('palatal','-cor,-back,-ant'),
                            ('velar','-cor,-ant,+back,+high'),
                            ('uvular','-cor,-ant,+back,-high'),
                            ('glottal', '+glot_cl,-cor,-ant'),]
        self.col_names = ['labial', 'dental', 'coronal', 'palatal', 'velar', 'uvular', 'glottal']
        self.row_names = ['stop', 'nasal', '-son nasal', 'fricative', 'lateral', 'approximant']
        self.display_matrix = {rname:{cname:list() for cname in self.col_names} for rname in self.row_names}
        self.display_matrix['nomatch'] = list()


class ResultsWindow(Toplevel):
    def __init__(self, title, headerline, master=None, delete_method=None, **options):
        if 'main_cols' in options:
            #Used for TableView
            main_cols = options.get('main_cols')
            del options['main_cols']
        else:
            main_cols = None
        super(ResultsWindow, self).__init__(master=master, **options)

        self.title(title)

        self._table = TableView(self,headerline,main_cols = main_cols)
        self._table.pack(expand=True,fill='both')
        if delete_method is not None:
            self.delete_results = delete_method
        self.protocol('WM_DELETE_WINDOW', self.delete_results)

        button_frame = Frame(self)
        print_button = Button(button_frame, text='Save results to file', command=self.save_results)
        print_button.grid(row=0, column=0)
        close_button = Button(button_frame, text='Close this table', command=self.delete_results)
        close_button.grid(row=0, column=1)
        button_frame.pack(side= 'bottom')


    def delete_results(self):
        self.destroy()

    def save_results(self):
        filename = FileDialog.asksaveasfilename()
        if not filename.endswith('.txt'):
            filename += '.txt'
        with open(filename, mode='w', encoding='utf-8') as f:
            print('\t'.join([h for h in self._table.headers]), file=f)
            for result in self._table.rows:
                print('\t'.join(str(r) for r in result)+'\r\n', file=f)

    def update(self, resultline):
        self._table.append(resultline)


class ThreadedTask(threading.Thread):
    def __init__(self, queue, target, args, **kwargs):
        if kwargs:
            threading.Thread.__init__(self,target=target, args=args, kwargs=kwargs['kwargs'])
        else:
            threading.Thread.__init__(self,target=target, args=args)
        self.queue = queue

class MultiListbox(Frame):
    def __init__(self, master, columns,main_cols=None):
        #Compatability check
        if main_cols is None:
            main_cols = list()
        if isinstance(columns[0],tuple):
            columns = [x[0] for x in columns]
        self._headers = tuple(columns)
        self._labels = []
        self._lbs = []
        Frame.__init__(self, master)

        self.grid_rowconfigure(1,weight=1)

        for i, h in enumerate(self._headers):
            if i not in main_cols:
                self.grid_columnconfigure(i,minsize=len(h),weight=1)
                l = Label(self, text=h, borderwidth=1, relief=RAISED)
                lb = Listbox(self, borderwidth=1, selectborderwidth=0,relief=FLAT, exportselection=False)

            else:
                self.grid_columnconfigure(i,minsize=len(h),weight=0)
                l = Label(self, text=h, borderwidth=1, relief=RAISED,width=len(h))
                lb = Listbox(self, borderwidth=1,width=len(h), selectborderwidth=0,relief=FLAT, exportselection=False)

            self._labels.append(l)
            l.grid(column = i, row=0, sticky='news', padx=0, pady=0)
            l.column_index = i
            #l.bind('<Button-1>', self._resize_column)

            self._lbs.append(lb)
            lb.grid(column=i, row=1, sticky='news', padx=0, pady=0)
            lb.column_index = i

            lb.bind('<B1-Motion>', self._select)
            lb.bind('<Button-1>', self._select)
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
            lb.bind('<MouseWheel>', lambda e: self._scroll(e.delta))

            #lb.unbind_all('<MouseWheel>')

        #self.bind('<Button-1>', self._resize_column)
        self.bind('<Up>', lambda e: self.select(delta=-1))
        self.bind('<Down>', lambda e: self.select(delta=1))
        self.bind('<Prior>', lambda e: self.select(delta=-self._pagesize()))
        self.bind('<Next>', lambda e: self.select(delta=self._pagesize()))

    @property
    def column_labels(self):
        """
        A tuple containing the ``Tkinter.Label`` widgets used to
        display the label of each column.  If this multi-column
        listbox was created without labels, then this will be an empty
        tuple.  These widgets will all be augmented with a
        ``column_index`` attribute, which can be used to determine
        which column they correspond to.  This can be convenient,
        e.g., when defining callbacks for bound events.
        """
        return tuple(self._labels)

    @property
    def headers(self):
        """
        A tuple containing the names of the columns used by this
        multi-column listbox.
        """
        return self._headers

    @property
    def listboxes(self):
        """
        A tuple containing the ``Tkinter.Listbox`` widgets used to
        display individual columns.  These widgets will all be
        augmented with a ``column_index`` attribute, which can be used
        to determine which column they correspond to.  This can be
        convenient, e.g., when defining callbacks for bound events.
        """
        return tuple(self._lbs)

    def _select(self, e):
        i = e.widget.nearest(e.y)
        self.selection_clear(0, 'end')
        self.selection_set(i)
        return 'break'

    def _button2(self, x, y):
        for l in self._lbs:
            l.scan_mark(x, y)
        return 'break'

    def _b2motion(self, x, y):
        for l in self._lbs:
            l.scan_dragto(x, y)
        return 'break'

    def _scrollbar(self, *args):
        for l in self._lbs:
            l.yview(*args)

    def _scroll(self, delta):
        if delta > 0:
            delta = -1
        else:
            delta = 1
        for l in self._lbs:
            l.yview_scroll(delta,'units')
        return 'break'

    def _resize_column(self, event):
        """
        Callback used to resize a column of the table.  Return ``True``
        if the column is actually getting resized (if the user clicked
        on the far left or far right 5 pixels of a label); and
        ``False`` otherwies.
        """
        # If we're already waiting for a button release, then ignore
        # the new button press.
        if event.widget.bind('<ButtonRelease>'):
            return False

        # Decide which column (if any) to resize.
        self._resize_column_index = None
        if event.widget is self:
            for i, lb in enumerate(self._listboxes):
                if abs(event.x-(lb.winfo_x()+lb.winfo_width())) < 10:
                    self._resize_column_index = i
        elif event.x > (event.widget.winfo_width()-5):
            self._resize_column_index = event.widget.column_index
        elif event.x < 5 and event.widget.column_index != 0:
            self._resize_column_index = event.widget.column_index-1

        # Bind callbacks that are used to resize it.
        if self._resize_column_index is not None:
            event.widget.bind('<Motion>', self._resize_column_motion_cb)
            event.widget.bind('<ButtonRelease-%d>' % event.num,
                              self._resize_column_buttonrelease_cb)
            return True
        else:
            return False

    def _resize_column_motion_cb(self, event):
        lb = self._lbs[self._resize_column_index]
        charwidth = lb.winfo_width() / lb['width']

        x1 = event.x + event.widget.winfo_x()
        x2 = lb.winfo_x() + lb.winfo_width()

        lb['width'] = max(3, lb['width'] + int((x1-x2)/charwidth))

    def _resize_column_buttonrelease_cb(self, event):
        event.widget.unbind('<ButtonRelease-%d>' % event.num)
        event.widget.unbind('<Motion>')

    def _pagesize(self):
        """:return: The number of rows that makes up one page"""
        return int(self.index('@0,1000000')) - int(self.index('@0,0'))

    def curselection(self):
        return self._lbs[0].curselection()

    def delete(self, first, last=None):
        for l in self._lbs:
            l.delete(first, last)

    def get(self, first, last=END):
        result = []
        for l in self._lbs:
            result.append(l.get(first,last))

        return result

##    def __len__(self):
##        return self.size()

    def index(self, index):
        self._lbs[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self._lbs:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self._lbs[0].size()

    def see(self, index):
        for l in self._lbs:
            l.see(index)

    def selection_anchor(self, index):
        for l in self._lbs:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self._lbs:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self._lbs[0].selection_includes(index)

    def selection_set(self, first, last=None):
        for l in self._lbs:
            l.selection_set(first, last)

    def yview(self, *args, **kwargs):
        for lb in self._lbs:
            v = lb.yview(*args, **kwargs)
        return v # if called with no arguments

    def yview_moveto(self, *args, **kwargs):
        for lb in self._lbs:
            lb.yview_moveto(*args, **kwargs)

    def yview_scroll(self, *args, **kwargs):
        for lb in self._lbs:
            lb.yview_scroll(*args, **kwargs)


class TableView(object):
    def __init__(self, master, column_names, rows = None, main_cols = None):
        #Compatability check
        if isinstance(column_names[0],tuple):
            column_names = [x[0] for x in column_names]
        if main_cols is None:
            main_cols = list()
        self._num_columns = len(column_names)
        self._column_mapping = {x:i for i,x in enumerate(column_names)}
        self._frame = Frame(master)

        if rows is None:
            self._rows = []
        else:
            self._rows = [[v for v in row] for row in rows]
        self._all_rows = self._rows

        try:
            main_cols = [self._column_mapping[x] for x in main_cols]
        except KeyError:
            main_cols = []
        self._mlistbox = MultiListbox(self._frame, column_names,main_cols)


        sb = Scrollbar(self._frame, orient='vertical',
                           command=self._mlistbox.yview)
        self._mlistbox.listboxes[0]['yscrollcommand'] = sb.set
        #for listbox in self._mlb.listboxes:
        #    listbox['yscrollcommand'] = sb.set
        sb.pack(side='right', fill='y')
        self._scrollbar = sb
        self._mlistbox.pack(side='left',expand=True, fill='both')

        self._sortkey = None
        for i, l in enumerate(self._mlistbox.column_labels):
            l.bind('<Button-1>', self._sort)

        self._populate()

    @property
    def headers(self):
        """A list of the names of the columns in this table."""
        return self._mlistbox.headers

    @property
    def rows(self):
        return self._rows

    def insert(self, row_index, rowvalue):
        """
        Insert a new row into the table, so that its row index will be
        ``row_index``.  If the table contains any rows whose row index
        is greater than or equal to ``row_index``, then they will be
        shifted down.

        :param rowvalue: A tuple of cell values, one for each column
            in the new row.
        """
        self._rows.insert(row_index, rowvalue)
        self._mlistbox.insert(row_index, rowvalue)

    def extend(self, rowvalues):
        """
        Add new rows at the end of the table.

        :param rowvalues: A list of row values used to initialze the
            table.  Each row value should be a tuple of cell values,
            one for each column in the row.
        """
        for rowvalue in rowvalues: self.append(rowvalue)

    def append(self, rowvalue):
        """
        Add a new row to the end of the table.

        :param rowvalue: A tuple of cell values, one for each column
            in the new row.
        """
        self.insert(len(self._rows), rowvalue)

    def clear(self):
        """
        Delete all rows in this table.
        """
        self._rows = []
        self._mlistbox.delete(0, 'end')

    def __getitem__(self, index):
        """
        Return the value of a row or a cell in this table.  If
        ``index`` is an integer, then the row value for the ``index``th
        row.  This row value consists of a tuple of cell values, one
        for each column in the row.  If ``index`` is a tuple of two
        integers, ``(i,j)``, then return the value of the cell in the
        ``i``th row and the ``j``th column.
        """
        if isinstance(index, tuple) and len(index)==2:
            return self._rows[index[0]][index[1]]
        else:
            return tuple(self._rows[index])

    def __setitem__(self, index, val):
        """
        Replace the value of a row or a cell in this table with
        ``val``.

        If ``index`` is an integer, then ``val`` should be a row value
        (i.e., a tuple of cell values, one for each column).  In this
        case, the values of the ``index``th row of the table will be
        replaced with the values in ``val``.

        If ``index`` is a tuple of integers, ``(i,j)``, then replace the
        value of the cell in the ``i``th row and ``j``th column with
        ``val``.
        """


        # table[i,j] = val
        if isinstance(index, tuple) and len(index)==2:
            i, j = index[0],index[1]
            self._rows[i][j] = val
            self._mlb.listboxes[j].insert(i, val)
            self._mlb.listboxes[j].delete(i+1)

        # table[i] = val
        else:
            self._rows[index] = list(val)
            self._mlistbox.insert(index, val)
            self._mlistbox.delete(index+1)

    def __delitem__(self, row_index):
        """
        Delete the ``row_index``th row from this table.
        """
        del self._rows[row_index]
        self._mlistbox.delete(row_index)

    def __len__(self):
        """
        :return: the number of rows in this table.
        """
        return len(self._rows)

    def _populate(self):
        self._mlistbox.delete(0, 'end')
        for i, row in enumerate(self._rows):
            self._mlistbox.insert('end', row)

    def pack(self, *args, **kwargs):
        self._frame.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        self._frame.grid(*args, **kwargs)

    def focus(self):
        self._mlistbox.focus()

    def bind(self, sequence=None, func=None, add=None):
        self._mlistbox.bind(sequence, func, add)

    def rowconfigure(self, row_index, cnf={}, **kw):
        self._mlistbox.rowconfigure(row_index, cnf, **kw)

    def columnconfigure(self, col_index, cnf={}, **kw):
        self._mlistbox.columnconfigure(col_index, cnf, **kw)

    def itemconfigure(self, row_index, col_index, cnf=None, **kw):
        return self._mlistbox.itemconfigure(row_index, col_index, cnf, **kw)

    def bind_to_labels(self, sequence=None, func=None, add=None):
        return self._mlistbox.bind_to_labels(sequence, func, add)

    def bind_to_listboxes(self, sequence=None, func=None, add=None):
        return self._mlistbox.bind_to_listboxes(sequence, func, add)

    def bind_to_columns(self, sequence=None, func=None, add=None):
        return self._mlistbox.bind_to_columns(sequence, func, add)

    def show_column(self, column_index):
        """:see: ``MultiListbox.show_column()``"""
        self._mlistbox.show_column(column_index)

    def hide_column(self, column_index):
        """:see: ``MultiListbox.hide_column()``"""
        self._mlistbox.hide_column(column_index)

    def selected_row(self):
        """
        Return the index of the currently selected row, or None if
        no row is selected.  To get the row value itself, use
        ``table[table.selected_row()]``.
        """
        sel = self._mlistbox.curselection()
        if sel:
            return int(sel[0])
        return None

    def select(self, index=None, delta=None, see=True):
        """:see: ``MultiListbox.select()``"""
        self._mlistbox.select(index, delta, see)

    def filter_by_in(self, **kwargs):
        for k,v in kwargs.items():
            try:
                c = self._column_mapping[k]
            except KeyError:
                continue
            if v:
                self._rows = [x for x in self._all_rows if x[c] in v]
            else:
                self._rows = self._all_rows
        self._populate()

    def sort_by(self, column_index):

        selection = self.selected_row()
        if column_index == self._sortkey:
            self._rows.reverse()
        else:
            self._rows.sort(key=operator.itemgetter(column_index),
                reverse=False)
            self._sortkey = column_index # Redraw the table.
        self._populate()
        for r, row in enumerate(self._rows):
            if id(row) == selection:
                self._mlistbox.select(r, see=see)
                break

    def _sort(self, event):
        """Event handler for clicking on a column label -- sort by
        that column."""
        column_index = event.widget.column_index

        # If they click on the far-left of far-right of a column's
        # label, then resize rather than sorting.
        #if self._mlistbox._resize_column(event):
        #    return 'continue'

        # Otherwise, sort.
        #else:
        #    self.sort_by(column_index)
        #    return 'continue'
        self.sort_by(column_index)
        return 'continue'

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
