from .imports import *
from .widgets import SegmentSelectionWidget, SegmentSelectDialog
from corpustools.corpus.classes.lexicon import EnvironmentFilter, SyllableEnvironmentFilter
import sip
from pprint import pprint
import regex as re

SPECIAL_SYMBOL_RE = ['.', '^', '$', '*', '+', '?', '|', '{', '}', '[', ']', '#', '(', ')', '\'', '\"']