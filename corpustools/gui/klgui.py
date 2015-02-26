#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Scott
#
# Created:     12/01/2015
# Copyright:   (c) Scott 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from corpustools.corpus.classes import Corpus
from corpustools.corpus.io import load_binary
import argparse
from math import log
from collections import defaultdict, OrderedDict
import os
from codecs import open

from .imports import *
from .widgets import SegmentPairSelectWidget, RadioSelectWidget
from .windows import FunctionWorker, FunctionDialog
from corpustools.kl.kl import KullbackLeibler

class KLWorker(FunctionWorker):
    def run(self):
        time.sleep(0.1)
        kwargs = self.kwargs
        self.results = list()
        for pair in kwargs['segment_pairs']:
            res = KullbackLeibler(kwargs['corpus'],
                            pair[0], pair[1],
                            outfile = None,
                            side = kwargs['side'],
                            stop_check = kwargs['stop_check'],
                            call_back = kwargs['call_back'])
            self.results.append(res)
        self.dataReady.emit(self.results)

class KLDialog(FunctionDialog):
    header = ['Segment 1',
                'Segment 2',
                'Context',
                'Segment 1 entropy',
                'Segment 2 entropy',
                'KL',
                'Possible UR',
                'Spurious allophones?'
                ]

    _about = [('This function calculates a difference in distribution of two segments'
                    ' based on the Kullback-Leibler measurement of the difference between'
                    ' probability distributions.'),
                    '',
                    'Coded by Scott Mackie',
                    '',
                    'References',
                    ('Sharon Peperkamp, Rozenn Le Calvez, Jean-Pierre Nadal, Emmanuel Dupoux. '
                    '2006. The Acquisition of allophonic rules: Statistical learning with linguistic constraints '
                    ' Cognition 101 B31-B41')]

    name = 'Kullback-Leibler'



    def __init__(self, parent, corpus, showToolTips):
        FunctionDialog.__init__(self, parent, KLWorker())

        self.corpus = corpus
        self.showToolTips = showToolTips

        klframe = QFrame()
        kllayout = QHBoxLayout()

        self.segPairWidget = SegmentPairSelectWidget(corpus.inventory)
        kllayout.addWidget(self.segPairWidget)

        self.side = str()
        self.contextRadioWidget = RadioSelectWidget('Contexts to examine',
                                                    OrderedDict([('Left-hand side only','lhs'),
                                                        ('Right-hand side only', 'rhs'),
                                                        ('Both sides', 'both')]),
                                                        #('All', 'all')]),
                                                        )
        kllayout.addWidget(self.contextRadioWidget)


        klframe.setLayout(kllayout)
        self.layout().insertWidget(0, klframe)


    def calc(self):
        kwargs = self.generateKwargs()
        if kwargs is None:
            return
        self.thread.setParams(kwargs)
        self.thread.start()

        result = self.progressDialog.exec_()

        self.progressDialog.reset()
        if result:
            self.accept()

    def generateKwargs(self):
        kwargs = {}
        segPairs = self.segPairWidget.value()
        if len(segPairs) == 0:
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify at least one segment pair.")
            return None
        kwargs['segment_pairs'] = segPairs
        kwargs['corpus'] = self.corpus
        kwargs['side'] = self.contextRadioWidget.value()[0]

        return kwargs
