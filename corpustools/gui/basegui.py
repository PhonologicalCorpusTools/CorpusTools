import threading
from tkinter import (Toplevel, Frame, Listbox, Scrollbar, END, BOTH, LEFT,
                    YES, X, FALSE, VERTICAL, Y, RAISED, FLAT, Label)

class AboutWindow(Toplevel):
    pass
    
class FunctionWindow(Toplevel):
    pass
    

class ResultsWindow(Toplevel):
    def __init__(self, title,headerline,master=None, **options):
        super(ResultsWindow, self).__init__(master=master, **options)
        
        self.title(title)

        self.as_results_table = MultiListbox(self,headerline)
        self.as_results_table.grid()

        button_frame = Frame(self)
        print_button = Button(button_frame, text='Save results to file', command=self.save_results)
        print_button.grid(row=0, column=0)
        close_button = Button(button_frame, text='Close this table', command=self.delete_results)
        close_button.grid(row=0, column=1)
        button_frame.grid()

    def delete_results(self):
        self.destroy()

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
