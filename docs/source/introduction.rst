.. _introduction:

************
Introduction
************


.. _PCT website: http://phonologicalcorpustools.github.io/CorpusTools/

.. _GitHub repository: https://github.com/PhonologicalCorpusTools/CorpusTools/

.. _kathleen.hall@ubc.ca: kathleen.hall@ubc.ca

.. _general_background:

General Background
==================

*Phonological CorpusTools* (PCT) is a freely available open-source tool
for doing phonological analysis on transcribed corpora.
For the latest information, please refer to the `PCT website`_. PCT is intended to be an
analysis aid for researchers who are specifically interested in
investigating the relationships that may hold between individual
sounds in a language. There is an ever-increasing interest in
exploring the roles of frequency and usage in understanding
phonological phenomena (e.g., [Bybee2001]_, [Ernestus2011]_, [Frisch2011]_),
but many corpora and existing corpus-analysis software tools are focused
on dialogue- and sentence-level analysis, and/or the computational skills
needed to efficiently handle large corpora can be daunting to learn.

PCT is designed with the phonologist in mind and has an easy-to-use
graphical user interface that requires no programming knowledge, though
it can also be used with a command-line interface,1 and all of the original
code is freely available for those who would like access to the source.
It specifically includes the following capabilities:

* Summary descriptions of a corpus, including type and token frequency of
  individual segments in user-defined environments;
* Calculation of the **phonotactic probability** of a word, given the other
  words that exist in the corpus (cf. [Vitevitch2004]_);
* Calculation of **functional load** of individual pairs of sounds,
  defined at either the segment or feature level (cf. [Hockett1966]_;
  [Surendran2003]_; [Wedel2013]_);
* Calculation of the extent to which any pair of sounds is **predictably
  distributed** given a set of environments that they can occur in, as a
  measure of phonological contrastiveness (cf. [Hall2009]_, [Hall2012]_; [Hall2013a]_);
* Calculation of the **Kullback-Leibler divergence** between the distributions
  of two sounds, again as a measure of phonological contrastiveness
  (cf. [Peperkamp2006]_);
* Calculation of the extent to which pairs of words are **similar** to each
  other using either orthographic or phonetic transcription,
  and calculation of **neighbourhood density** (cf. [Frisch2004]_, [Khorsi2012]_;
  [Greenberg1964]_; [Luce1998]_; [Yao2011]_);
* Approximation of the **frequency with which two sounds alternate** with each other,
  given a measure of morphological relatedness (cf. [Silverman 2006]_,
  [Johnson2010]_, [Lu2012]_);
* Calculation of the **mutual information** between pairs of segments in the corpus
  (cf. [Brent1999]_; [Goldsmith2012]_); and
* Calculation of the **acoustic similarity** between sounds or words,
  derived from sound files, based on alignment of MFCCs (e.g., [Mielke2012]_)
  or of logarithmically spaced amplitude envelopes (cf. [Lewandowski2012]_).

The software can make use of pre-existing freely available corpora
(e.g., the IPHOD corpus; [IPHOD]_), which are included with the
system, or a user may upload his or her own corpus in several formats.
First, lexical lists with transcription and token frequency information can be
directly uploaded; such a list is what is deemed a “corpus” by PCT. Second,
raw running text (orthographically and/or phonetically transcribed) can be
uploaded and turned into lexical lists in columnar format (corpora) for
subsequent analysis. Raw sound files accompanied by Praat TextGrids
[PRAAT]_ may also be uploaded for analyses of acoustic
similarity, and certain pre-existing special types of corpora can be uploaded natively (Buckeye [BUCKEYE]_, TIMIT [TIMIT]_). Orthographic corpora can have their transcriptions “looked up”
in a pre-existing transcribed corpus of the same language.

Phonological analysis can be done using built-in feature charts based on
Chomsky & Halle [SPE]_ or Hayes [Hayes2009]_, or a user may create his or her
own specifications by either modifying these charts or uploading a new chart.
Feature specifications can be used to pull out separate “tiers” of segments for
analysis (e.g., consonants vs. vowels, all nasal elements, tonal contours, etc.).
PCT comes with IPA transcription installed, with characters mapped to the two feature
systems mentioned above. Again, users may create their own transcription-to-feature
mappings by modifying the existing ones or uploading a new transcription-to-feature
mapping file, and several alternative transcription-to-feature mapping files are
available for download.

Analysis can be done using type or token frequency, if token frequency is
available in the corpus. All analyses are presented both on screen and
saved to plain .txt files in user-specfied locations.

The following sections walk through the specifics of downloading, installing,
and using the various components of Phonological CorpusTools.
We will do our best to keep the software up to date and to answer any questions
you might have about it; questions, comments, and suggestions should be sent to
`Kathleen Currie Hall <kathleen.hall@ubc.ca>`_.

Version 1.2 (July 2016) differs from version 1.1 (July 2015) in the following areas:

1. Inventory management -- The tools for categorizing segments into an inventory chart have been updated to allow users to interactively update the chart based on nature classes, including the ability to add / delete / rearrange columns and rows in the chart. Uncategorized segments are more clearly shown and their features easily examined for reference.

2. Increased flexibility -- Environments can be more flexibly defined, e.g., using wildcards and inserting / modifying / deleting segments or classes of segments within a linear string. Within the functional load analysis, functional load can be calculated within individual sets of environments rather than exclusively at the word level.

3. Small updates for usability -- Numerous small updates have been implemented to aid usability, such as improving the ability to select segments based on features, returning results that list features if those were used in the selection of segments, updating the documentation for clarity, adding an option for normalizing functional load results, etc.

Version 1.1 (July 2015) differs from version 1.0.1 (March 2015) in three main areas:

1. Loading of corpora -- The interface for corpus loading has been streamlined,
   and users have more options for adjusting the interpretation of transcriptions
   and columns as they initiate a corpus. Better support for interlinear glosses
   and TextGrids is also provided.

2. Specification of inventories, features, and environments -- Inventories
   can now be displayed in IPA-like charts based on user-specified features.
   Feature selection in analysis functions has been streamlined and natural
   class selection is better supported. Environment selection is now iterative
   and more interactive.

3. Pronunciation variants -- Analysis functions now provide users with
   options for how to handle pronunciation variants when they occur in a corpus.

Version 1.0 differs from the original release version (0.15, July 2014)
primarily in its user interface; we switched the GUI from TK to QT and
tried to reorganize the utility menus to be somewhat more intuitive.
For example, the original release version had all segment inventory views
in alphabetical order; segments are now arranged as closely as possible to
standard IPA chart layouts (based on their featural interpretations).
Additionally, we have added greater search and edit functions as well as
some additional analysis tools (phonotactic probability, mutual information,
neighbourhood density), and a greater ability to work with running text /
spontaneous speech corpora.

.. _code_and_interfaces:

Code and interfaces
===================

PCT is written in Python 3.4, and users are welcome to add on other
functionality as needed. The software works on any platform that supports
Python (Windows, Mac, Linux). All code is available on the
`GitHub repository`_; the details for
getting access are given in :ref:`downloading_and_installing`.

There is both a graphical user interface (GUI) and a command-line interface
for PCT. In the following sections, we generally discuss interface-independent
aspects of some functionality first, and then detail how to implement it in
both the GUI and the command line. All functions are available in the GUI;
many, but not all, are currently available in the command line due to
complications in entering in phonological transcriptions that match a
given corpus in a command-line interface.

The command-line interface is accessed using command line scripts that are
installed on your machine along with the core PCT GUI.

**NOTE**: If you did not install PCT on your computer but are instead running
the GUI through a binary file (executable), then the command line scripts
are not installed on your computer either. In order to run them, you will
need to download the PCT source code and then find the scripts within the
command_line subdirectory. These can then be run as scripts in Python 3.

The procedure for running command-line analysis scripts is essentially the
same for any analysis. First, open a Terminal window (on Mac OS X or Linux)
or a CygWin window (on Windows, can be downloaded at `https://www.cygwin.com/ <https://www.cygwin.com/>`_).
Using the "cd" command, navigate to the directory containing your corpus file.
If the analysis you want to perform requires any additional input files, then
they must also be in this directory. (Instead of running the script from the
relevant file directory, you may also run scripts from any working directory as
long as you specify the full path to any files.) You then type the analysis
command into the Terminal and press enter/return to run the analysis. The first
(positional) argument after the name of the analysis script is always the name
of the corpus file.
