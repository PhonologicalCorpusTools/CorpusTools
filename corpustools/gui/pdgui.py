import os

from tkinter import (LabelFrame, Label, W, Entry, Button, Radiobutton,
                    Frame, StringVar, BooleanVar, END, DISABLED, TclError,
                    ACTIVE, IntVar,OptionMenu,Checkbutton, N,Listbox,
                    LEFT, E, RIGHT)
from tkinter import Radiobutton as OldRadiobutton
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import queue
from math import log

import corpustools.prod.pred_of_dist as PD

from corpustools.gui.basegui import (AboutWindow, FunctionWindow, ERROR_DIR,
                    ResultsWindow, MultiListbox, ThreadedTask, ToolTip)

class PDFunction(FunctionWindow):
    def __init__(self,corpus, master=None, **options):
        super(PDFunction, self).__init__(master=master, **options)

        self.corpus = corpus
        #entropy calculation variables
        self.entropy_tier_var = StringVar()
        self.entropy_typetoken_var = StringVar()
        self.letter1_var = StringVar()
        self.letter2_var = StringVar()
        self.seg1_var = StringVar()
        self.seg2_var = StringVar()
        self.lhs_feature_var = StringVar()
        self.rhs_feature_var = StringVar()
        self.lhs_seg_var = StringVar()
        self.rhs_seg_var = StringVar()
        self.entropy_filename_var = StringVar()
        self.entropy_exhaustive_var = IntVar()
        self.entropy_uniqueness_var = IntVar()
        self.entropy_exclusive_var = IntVar()
        self.prod_results = None
        self.calculating_entropy_screen = None

        self.ipa_frame = None
        self.option_frame = None
        self.button_frame = None

        self.env_frame = None
        self.selected_envs_frame = None

        self.show_segment_screen()

        self.focus()

    def remove_frames(self):
        if self.ipa_frame is not None:
            self.ipa_frame.destroy()
            self.ipa_frame = None

        if self.option_frame is not None:
            self.option_frame.destroy()
            self.option_frame = None

        if self.button_frame is not None:
            self.button_frame.destroy()
            self.button_frame = None

        if self.env_frame is not None:
            self.env_frame.destroy()
            self.env_frame = None

        if self.selected_envs_frame is not None:
            self.selected_envs_frame.destroy()
            self.selected_envs_frame = None


    def show_segment_screen(self):
        self.remove_frames()
        self.title('Predictability of distribution calculation')
        #check if it's possible to do this analysis

        self.ipa_frame = LabelFrame(self, text='Sounds')

        ipa_frame_tooltip = ToolTip(self.ipa_frame,follow_mouse=True,
                                    text=('Choose the two sounds whose '
        'predictability of distribution you want to calculate. The order of the '
        'two sounds is irrelevant. The symbols you see here should automatically'
        ' match the symbols used anywhere in your corpus.'))
        segs = [seg.symbol for seg in self.corpus.get_inventory()]
        segs.sort()
        seg1_frame = LabelFrame(self.ipa_frame, text='Choose first symbol')
        colmax = 10
        col = 0
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(seg1_frame, text=seg, variable=self.seg1_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        seg1_frame.grid()

        seg2_frame = LabelFrame(self.ipa_frame, text='Choose second symbol')
        colmax = 10
        col = 0
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(seg2_frame, text=seg, variable=self.seg2_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        seg2_frame.grid()


        self.option_frame = LabelFrame(self, text='Options')

        tier_frame = LabelFrame(self.option_frame, text='Tier')
        tier_frame_tooltip = ToolTip(tier_frame, follow_mouse=True,
                                    text=('Choose which tier predictability should'
                                    'be calculated over (e.g., the whole transcription'
                                    ' vs. a tier containing only [+voc] segments).'
                                    'New tiers can be created from the Corpus menu.'))
        tier_options = ['transcription']
        word = self.corpus.random_word()
        tier_options.extend([tier for tier in word.tiers])
        tier_options_menu = OptionMenu(tier_frame,self.entropy_tier_var,*tier_options)
        tier_options_menu.grid()
        tier_frame.grid(row=0,column=0)
        
        self.entropy_tier_var.set(tier_options[0])

        typetoken_frame = LabelFrame(self.option_frame, text='Type or Token')
        typetoken_tooltip = ToolTip(typetoken_frame, follow_mouse=True,
                                    text=('Choose what kind of frequency should '
                                    'be used for the calculations. Type frequency'
                                    ' means each word is counted once. Token frequency'
                                    ' means each word is counted as often as it occurs'
                                    ' in the corpus.'))
        type_button = Radiobutton(typetoken_frame, text='Count types', variable=self.entropy_typetoken_var, value='type')
        type_button.grid(sticky=W)
        type_button.invoke()
        token_button = Radiobutton(typetoken_frame, text='Count tokens', variable=self.entropy_typetoken_var, value='token')
        token_button.grid(sticky=W)
        if not self.corpus.has_frequency():
            token_button.configure(state=('disabled'))
        typetoken_frame.grid(row=1, column=0)

        ex_frame = LabelFrame(self.option_frame, text='Exhaustivity and uniqueness')
        ex_frame_tooltip = ToolTip(ex_frame, follow_mouse=True,
                                    text=('Indicate whether you want the program'
                                    ' to check for exhausitivity and/or uniqueness.'
                                    ' Checking for exhaustivity means the program '
                                    'will make sure that you have selected environments'
                                    ' that cover all instances of the two sounds in the'
                                    ' corpus. Checking for uniqueness means the program'
                                    ' will check to make sure that the environments you'
                                    ' have selected don\'t overlap with one another. It'
                                    ' is recommended that both options are used unless '
                                    'there is a specific reason to do otherwise.'))
        check_exhaustive = Checkbutton(ex_frame, text='Check for exhaustivity', variable=self.entropy_exhaustive_var)
        self.entropy_exhaustive_var.set(1)
        check_exhaustive.grid()
        check_uniqueness = Checkbutton(ex_frame, text='Check for uniqueness', variable=self.entropy_uniqueness_var)
        check_uniqueness.grid()
        self.entropy_uniqueness_var.set(1)
        ex_frame.grid(row=2, column=0)

        self.button_frame = Frame(self)
        ok_button = Button(self.button_frame, text='Next step...', command=self.show_environment_screen)
        ok_button.grid(row=0, column=0)
        cancel_button = Button(self.button_frame, text='Cancel', command=self.cancel_prod)
        cancel_button.grid(row=0, column=1)
        info_button = Button(self.button_frame, text='About this function...', command=self.about_prod)
        info_button.grid(row=0, column=2)

        self.ipa_frame.grid(row=0, column=0, sticky=N)
        self.option_frame.grid(row=0, column=1, sticky=N)
        self.button_frame.grid(row=1,column=0)

    def show_environment_screen(self):
        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()

        if not (seg1 and seg2):
            MessageBox.showerror(message='Please ensure you have selected 2 segments')
            return

        self.remove_frames()


        self.title('Environments for calculating predictability of distribution')


        self.env_frame = LabelFrame(self, text='Construct environment')
        env_frame_tooltip = ToolTip(self.env_frame, follow_mouse=False,
                                    text=('This screen allows you to construct multiple'
                                    ' environments in which to calculate predictability'
                                    ' of distribution. For each environment, you can specify'
                                    ' either the left-hand side or the right-hand side, or '
                                    'both. Each of these can be specified using either features or segments.'))

        lhs_frame = LabelFrame(self.env_frame, text='Left hand side')

        lhs_feature_frame = LabelFrame(lhs_frame, text='Feature-based environment')
        lhs_feature_entry_explanation = Label(lhs_feature_frame, text='Select one or more features to match')
        lhs_feature_entry_explanation.grid(row=0)
        self.lhs_feature_list = Listbox(lhs_feature_frame)
        for feature_name in self.corpus.get_features():
            self.lhs_feature_list.insert(END,feature_name)
        self.lhs_feature_list.grid(row=1, column=0)
        self.lhs_selected_list = Listbox(lhs_feature_frame)
        lhs_button_frame = Frame(lhs_feature_frame)
        add_plus = Button(lhs_button_frame, text='Add [+feature]', command=self.add_plus_feature_lhs)
        add_plus.grid(row=0,column=0)
        add_minus = Button(lhs_button_frame, text='Add [-feature]', command=self.add_minus_feature_lhs)
        add_minus.grid(row=1, column=0)
        clear_features = Button(lhs_button_frame, text='Clear list', command=lambda x=0:self.lhs_selected_list.delete(x,END))
        clear_features.grid(row=2, column=0)
        lhs_button_frame.grid(row=1,column=1)
        self.lhs_selected_list.grid(row=1, column=2)

        lhs_seg_frame = LabelFrame(lhs_frame, text='Segment-based environment')
        lhs_seg_entry_explanation = Label(lhs_seg_frame, text='Select a segment to match')
        lhs_seg_entry_explanation.grid()
        segs = [seg.symbol for seg in self.corpus.get_inventory()]
        segs.sort()
        segs_frame = Frame(lhs_seg_frame)
        col = 0
        colmax = 8
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(segs_frame, text=seg, variable=self.lhs_seg_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        segs_frame.grid()
        self.lhs_seg_entry = Entry(lhs_seg_frame,textvariable=self.lhs_seg_var)
        self.lhs_seg_entry.grid()

        lhs_feature_frame.grid(row=0, column=0, sticky=N)
        lhs_seg_frame.grid(row=0, column=1, sticky=N)
        lhs_frame.grid(row=0, column=0, padx=3)


        #RIGHT HAND SIDE STARTS HERE
        rhs_frame = LabelFrame(self.env_frame, text='Right hand side')

        rhs_feature_frame = LabelFrame(rhs_frame, text='Feature-based environment')
        rhs_feature_entry_explanation = Label(rhs_feature_frame, text='Select one or more features to match')
        rhs_feature_entry_explanation.grid(row=0)
        self.rhs_feature_list = Listbox(rhs_feature_frame)
        for feature_name in self.corpus.get_features():
            self.rhs_feature_list.insert(END,feature_name)
        self.rhs_feature_list.grid(row=1, column=0)
        self.rhs_selected_list = Listbox(rhs_feature_frame)
        rhs_button_frame = Frame(rhs_feature_frame)
        add_plus = Button(rhs_button_frame, text='Add [+feature]', command=self.add_plus_feature_rhs)
        add_plus.grid(row=0,column=0)
        add_minus = Button(rhs_button_frame, text='Add [-feature]', command=self.add_minus_feature_rhs)
        add_minus.grid(row=1, column=0)
        clear_features = Button(rhs_button_frame, text='Clear list', command=lambda x=0:self.rhs_selected_list.delete(x,END))
        clear_features.grid(row=2, column=0)
        rhs_button_frame.grid(row=1,column=1)
        self.rhs_selected_list.grid(row=1, column=2)

        rhs_seg_frame = LabelFrame(rhs_frame, text='Segment-based environment')
        rhs_seg_entry_explanation = Label(rhs_seg_frame, text='Select a segment to match')
        rhs_seg_entry_explanation.grid()
        segs = [seg.symbol for seg in self.corpus.get_inventory()]
        segs.sort()
        segs_frame = Frame(rhs_seg_frame)
        col = 0
        colmax = 8
        row = 0
        for seg in segs:
            seg_button = OldRadiobutton(segs_frame, text=seg, variable=self.rhs_seg_var, value=seg, indicatoron=0)
            seg_button.grid(row=row, column=col)
            col+=1
            if col > colmax:
                col = 0
                row += 1
        segs_frame.grid()
        self.rhs_seg_entry = Entry(rhs_seg_frame,textvariable=self.rhs_seg_var)
        self.rhs_seg_entry.grid()

        rhs_feature_frame.grid(row=0, column=0, sticky=N)
        rhs_seg_frame.grid(row=0, column=1, sticky=N)
        rhs_frame.grid(row=1, column=0, padx=3)
        add_env_to_list = Button(self.env_frame, text='Add this environment to list', command=self.confirm_environments)
        add_env_to_list.grid()#row=0, column=0)
        self.env_frame.grid(row=0, column=0)

        #SELECTED ENVIRONMENTS FRAME
        self.selected_envs_frame = Frame(self)
        selected_envs_label = Label(self.selected_envs_frame, text='Environments created so far:')
        selected_envs_label.grid()
        self.selected_envs_list = Listbox(self.selected_envs_frame)
        self.selected_envs_list.configure(width=40)
        self.selected_envs_list.grid()
        remove_env_button = Button(self.selected_envs_frame, text='Remove selected environment', command=self.remove_entropy_env)
        remove_env_button.grid()
        clear_envs = Button(self.selected_envs_frame, text='Remove all environments', command=lambda x=0:self.selected_envs_list.delete(x,END))
        clear_envs.grid()
        self.selected_envs_frame.grid(row=0, column=1)

        #BUTTON FRAME STARTS HERE
        self.button_frame = Frame(self)

        confirm_envs = Button(self.button_frame, text='Calculate entropy in selected environments and add to results table', command=self.calculate_prod)
        confirm_envs.grid(sticky=W)
        context_free = Button(self.button_frame, text='Calculate entropy across ALL environments and add to results table', command=self.calculate_prod_all_envs)
        context_free.grid(sticky=W)
        self.start_new_envs = Button(self.button_frame, text='Destroy results table', command=self.destroy_prod_results)
        self.start_new_envs.grid(sticky=W)
        self.start_new_envs.config(state=DISABLED)

        previous_step = Button(self.button_frame, text='Previous step', command=self.show_segment_screen)
        previous_step.grid(sticky=W)
        cancel_button = Button(self.button_frame, text='Cancel', command=self.destroy)
        cancel_button.grid(sticky=W)

        self.button_frame.grid(row=0,column=2)



    def calculate_prod_all_envs(self):
        if self.selected_envs_list.size() > 0:
            carry_on = MessageBox.askokcancel(message=('You have already selected some environments.\n'
                                        ' Click \'OK\' to do a calculation of entorpy across ALL environments.\n'
                                        ' Click \'Cancel\' to go back and use your specific environments.\n'))
            if not carry_on:
                return

        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()
        type_or_token = self.entropy_typetoken_var.get()
        seg1_count, seg2_count = PD.count_segs(self.corpus, seg1, seg2, type_or_token, self.entropy_tier_var.get())
        H = PD.calc_prod_all_envs(seg1_count, seg2_count)
        results = [[
            self.corpus.name,
            self.entropy_tier_var.get(),
            seg1,
            seg2,
            'FREQ-ONLY',
            str(seg1_count),
            str(seg2_count),
            str(seg1_count+seg2_count),
            str(H)]]
        self.update_prod_results(results)


    def remove_entropy_env(self):
        env = self.selected_envs_list.curselection()
        if env:
            self.selected_envs_list.delete(env)

    def add_plus_feature_lhs(self):
        try:
            feature_name = self.lhs_feature_list.get(self.lhs_feature_list.curselection())
            feature_name = '+'+feature_name
            self.lhs_selected_list.insert(END,feature_name)
        except TclError:
            pass

    def add_minus_feature_lhs(self):
        try:
            feature_name = self.lhs_feature_list.get(self.lhs_feature_list.curselection())
            feature_name = '-'+feature_name
            self.lhs_selected_list.insert(END,feature_name)
        except TclError:
            pass

    def add_plus_feature_rhs(self):
        try:
            feature_name = self.rhs_feature_list.get(self.rhs_feature_list.curselection())
            feature_name = '+'+feature_name
            self.rhs_selected_list.insert(END,feature_name)
        except TclError:
            pass


    def add_minus_feature_rhs(self):
        try:
            feature_name = self.rhs_feature_list.get(self.rhs_feature_list.curselection())
            feature_name = '-'+feature_name
            self.rhs_selected_list.insert(END,feature_name)
        except TclError:
            pass

    def confirm_environments(self):
        lhs_features_chosen = self.lhs_selected_list.get(0)
        lhs_seg_chosen = self.lhs_seg_entry.get()
        rhs_features_chosen = self.rhs_selected_list.get(0)
        rhs_seg_chosen = self.rhs_seg_entry.get()
        if (lhs_features_chosen and lhs_seg_chosen) or (rhs_features_chosen and rhs_seg_chosen):
            MessageBox.showerror(message='You have selected both features and segments for an environment. Please enter only one and clear the other.')
            return


        elif (not lhs_features_chosen) and (not lhs_seg_chosen) and (not rhs_features_chosen) and (not rhs_seg_chosen):
            #allow for no input on one side or the other, but not both
            MessageBox.showerror(message='Both sides of the environment are blank. Construct at least one side.')
            return

        formatted_env = list()

        if lhs_features_chosen:
            lhs_features = self.lhs_selected_list.get(0,END)
            formatted_env.append('[{}]'.format(','.join(lhs_features)))
            #self.selected_envs_list.insert(END,lhs_features)
            self.lhs_selected_list.delete(0,END)

        elif lhs_seg_chosen:
            lhs_seg = self.lhs_seg_entry.get()
            formatted_env.append(lhs_seg)
            #self.selected_envs_list.insert(END,lhs_seg)
            self.lhs_seg_entry.delete(0,END)

        else:
            formatted_env.append('')

        if rhs_features_chosen:
            rhs_features = self.rhs_selected_list.get(0,END)
            formatted_env.append('[{}]'.format(','.join(rhs_features)))
            #self.selected_envs_list.insert(END,rhs_features)
            self.rhs_selected_list.delete(0,END)

        elif rhs_seg_chosen:
            rhs_seg = self.rhs_seg_entry.get()
            formatted_env.append(rhs_seg)
            #self.selected_envs_list.insert(END,rhs_seg)
            self.rhs_seg_entry.delete(0,END)

        else:
            formatted_env.append('')

        formatted_env = '_'.join(formatted_env)
        self.selected_envs_list.insert(END,formatted_env)


    def check_for_uniquess_and_exhuastivity(self, missing_words, overlapping_words, env_list):

        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()

        if self.entropy_uniqueness_var.get() and overlapping_words:
            #envs are exhastive, but some overlap
            final = os.path.split(self.entropy_filename_var.get())[-1]
            filename = 'overlapping_envs_'+final
            with open(os.path.join(ERROR_DIR, filename), mode='w', encoding='utf-8') as f:

                print('The environments you selected are not unique, which means that some of them pick out the same environment in the same words.\r\n', file=f)
                print('For example, the environments of \'_[-voice]\' and \'_k\', are not unique. They overlap with each other, since /k/ is [-voice].\r\n',file=f)
                print('When your environments are not unique, the entropy calculation will be inaccurate, since some environments will be counted more than once.\r\n', file=f)
                print('This file contains all the words where this problem could arise.\r\n\r\n', file=f)
                print('Segments you selected: {}, {}\r'.format(seg1, seg2), file=f)
                print('Environments you selected: {}\r'.format(' ,'.join(str(env) for env in env_list)), file=f)
                print('Word\tRelevant environments (segmental level only)\r',file=f)
                for word in overlapping_words:
                    print('{}\t{}\r\n'.format(word,','.join([w for w in overlapping_words[word]])), file=f)

            text1 = 'Your environments are not unique, and two or more of them overlap.'
            text2 = 'This means that some environments will be counted more than once and your entropy values will not be reliable.'
            text3 = 'A text file called {} explaining this problem has been placed in your ERRORS folder ({})'.format(filename,ERROR_DIR)
            text4 = 'Do you want to carry on with the entropy calculation anyway?'
            do_entropy = MessageBox.askyesno(message='\n'.join([text1,text2,text3,text4]))
            if not do_entropy:
                return False

        if self.entropy_exhaustive_var.get() and missing_words:
            #environments are unique but non-exhaustive
            filename = 'missing_words_entropy_{}_and_{}.txt'.format(self.seg1_var.get(), self.seg2_var.get())
            with open(os.path.join(ERROR_DIR, filename), mode='w', encoding='utf-8') as f:

                print('The following words have at least one of the segments you are searching for, but it occurs in an environment not included in the list you selected\r', file=f)
                print('Segments you selected: {}, {}\r'.format(seg1, seg2), file=f)
                print('Environments you selected: {}\r'.format(' ,'.join(str(env) for env in env_list)), file=f)
                print('Word\tRelevant environments (segmental level only)\r',file=f)
                for word in missing_words:
                    line = '{}\t{}\r'.format(word, ','.join(str(wm) for wm in missing_words[word]))
                    print(line, file=f)

            if self.entropy_uniqueness_var.get() and overlapping_words:
                also = ' also '
            else:
                also = ' '
            text = 'Your selection of environments was{}non-exhaustive.'.format(also)
            text2 = 'This means some words contain the segments you selected, but they do not contain the environments you selected.'
            text3 = 'These words have been printed to the file {} in your ERRORS folder ({}).'.format(filename,ERROR_DIR)
            text4 = 'If you choose to carry on with the calculation, then environment-specific entropies will be accurate.'
            text5 = 'However, the weighted average entropy will not reflect the occurrence of the sounds in the non-included environments.'
            if self.entropy_uniqueness_var.get() and overlapping_words:
                text6 = 'The average will also not be accurate because your environments are non-unique.\nWould you still like to calculate entropy in the enviroments you supplied?'
            else:
                text6 = 'Would you still like to calculate entropy in the enviroments you supplied?'
            do_entropy = MessageBox.askyesno(message='\n\r'.join([text, text2, text3, text4, text5, text6]))
            if not do_entropy:
                return False

        #if we made it this far, the user has agreed with everything
        #or else there were no problems to begin with
        return True



    def calculate_prod(self):
        check = self.selected_envs_list.get(0)
        if not check:
            MessageBox.showwarning(message='Please construct at least one environment')
            return


        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()
        type_or_token = self.entropy_typetoken_var.get()

        env_list = [env for env in self.selected_envs_list.get(0,END)]
        env_matches, missing_words, overlapping_words = PD.check_envs(self.corpus,seg1,seg2,type_or_token,env_list,self.entropy_tier_var.get())
        do_entropy = self.check_for_uniquess_and_exhuastivity(missing_words, overlapping_words,env_list)
        if not do_entropy:
            return #user does not want to see the results

        #at this point there are either no problems
        #or else the user wants to see the results anyway

        results = PD.calc_prod(self.corpus.name, self.entropy_tier_var.get(), seg1, seg2, env_matches)
        self.update_prod_results(results)

    def suggest_entropy_filename(self):
        seg1 = self.seg1_var.get()
        seg2 = self.seg2_var.get()
        suggested_name = 'entropy_of_{}_{}_{}.txt'.format(seg1, seg2, self.entropy_typetoken_var.get())
        filename = FileDialog.asksaveasfilename(initialdir=os.getcwd(),
                                                initialfile=suggested_name,
                                                defaultextension='.txt')
        return filename

    def about_prod(self):
        about = AboutWindow('About the predictability of distribution function',
                ('This function calculates'
                ' the predictability of distribution of two sounds, using the measure of entropy'
                ' (uncertainty). Sounds that are entirely predictably distributed (i.e., in'
                ' complementary distribution, commonly assumed to be allophonic), will have'
                ' an entropy of 0. Sounds that are perfectly overlapping in their distributions'
                ' will have an entropy of 1.'),
                ['Hall, K.C. 2009. A probabilistic model of phonological relationships from contrast to allophony. PhD dissertation, The Ohio State University.'],
                ['Scott Mackie', 'Blake Allen'])

    def create_prod_results(self):
        header = [('Corpus', 10),
                ('Tier', 15),
                ('Sound1', 10),
                ('Sound2', 10),
                ('Environment',30),
                ('Frequency of Sound1', 10),
                ('Frequency of Sound2', 10),
                ('Total count',10),
                ('Entropy',10)]
        title = 'Predictability of distribution results'
        self.prod_results = ResultsWindow(title,header,delete_method=self.destroy_prod_results)

    def update_prod_results(self, results):
        if self.prod_results is None:
            self.create_prod_results()
        for result in results:
            self.prod_results.update(result)

    def cancel_prod(self):
        self.destroy_prod_results()
        self.destroy()

    def destroy_prod_results(self):
        try:
            self.prod_results.destroy()
            self.prod_results = None
        except (TclError, AttributeError):#widgets don't exist anyway
            pass
