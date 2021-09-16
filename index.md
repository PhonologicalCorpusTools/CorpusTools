### Note: the "tar.gz" and ".zip" links at the top of this page will download the individual program files, not the executable version of the software. The latest release of the executable can be found here: [https://github.com/PhonologicalCorpusTools/CorpusTools/releases](https://github.com/PhonologicalCorpusTools/CorpusTools/releases). More details on installation are below.


## About Phonological CorpusTools

There is an ever-increasing interest in exploring the roles of frequency and usage in understanding phonological phenomena (e.g., Bybee 2001, Ernestus 2011, Frisch 2011, Archangeli & Pulleyblank 2013, Hume et al. to appear). Corpora of language give us a way of making generalizations across wide swaths of such usage, exploring patterns in under-documented languages, and creating balanced stimuli in experiments, but:
* many corpora and analysis tools are focused on dialogue- and sentence-level analysis, rather than phonological analysis;
* the skills needed to efficiently handle large corpora can be daunting to learn; and
* researchers may be using different instantiations of the “same” formulae, making direct comparisons of phenomena difficult.

Phonological CorpusTools (PCT) is our answer to these problems -- a free, downloadable program with both a graphical and command-line interface, designed to be a search and analysis aid for dealing with questions of phonological interest in large corpora. 

An overview article about the software is available:

Hall, Kathleen Currie, J. Scott Mackie, and Roger Yu-Hsiang Lo. (2019). Phonological CorpusTools: Software for doing phonological analysis on transcribed corpora. International Journal of Corpus Linguistics 24(4). 522-535. https://doi.org/10.1075/ijcl.18009.hal

Various files related to PCT, including example corpus and feature files, are available at https://github.com/PhonologicalCorpusTools/PCT_Fileshare.

### Versions
#### Please always use the latest version of PCT! You can check for updates from within PCT ("Help" / "Check for updates...").
Version 1.4.1 was released in September 2019. This version sizes inventory tables in a more appropriate way, includes the version number in output tables for archival purposes, and fixes bugs in the phonological search, functional load, and "About PCT" functions. 

Version 1.4 was released in December 2018. It differs from v. 1.3 (July 2017) in the following areas:

1. Support for syllable structure has been added to the software, allowing searches based on stress or tone.
2. The functional load algorithm based on minimal pair counts has been FIXED -- previous versions returned counts based on token frequencies instead of type frequencies.
3. The feature values in the pre-included feature systems have been updated to fix corruption issues.
4. Functional load calculations with right-hand environment specifications should be working.

Smaller updates within 1.4 (e.g., 1.4.1) are to fix small issues in functionality but do not reflect major changes.

Version 1.3 was released in July 2017. It differs from v. 1.2 (December 2016) in the following areas:

1. An additonal analysis algorithm for calculating informativity has been added.
2. The options for relativizing functional load have been revised and clarified.
3. Numerous small usability fixes have been included.

Version 1.2 was released in December 2016. It differs from v. 1.1 (July 2015) in the following areas:

1. Inventory management -- The tools for categorizing segments into an inventory chart have been updated to allow users to interactively update the chart based on nature classes, including the ability to add / delete / rearrange columns and rows in the chart. Uncategorized segments are more clearly shown and their features easily examined for reference.

2. Increased flexibility -- Environments can be more flexibly defined, e.g., using wildcards and inserting / modifying / deleting segments or classes of segments within a linear string. Within the functional load analysis, functional load can be calculated within individual sets of environments rather than exclusively at the word level.

3. Small updates for usability -- Numerous small updates have been implemented to aid usability, such as improving the ability to select segments based on features, returning results that list features if those were used in the selection of segments, updating the documentation for clarity, adding an option for normalizing functional load results, etc.

Version 1.1 was released as of 6 July 2015. It differs from version 1.0.1 (March 2015) in three main areas:

1. Loading of corpora -- The interface for corpus loading has been streamlined, and users have more options for adjusting the interpretation of transcriptions and columns as they initiate a corpus. Better support for interlinear glosses and TextGrids is also provided.

2. Specification of inventories, features, and environments -- Inventories can now be displayed in IPA-like charts based on user-specified features. Feature selection in analysis functions has been streamlined and natural class selection is better supported. Environment selection is now iterative and more interactive.

3. Pronunciation variants -- Analysis functions now provide users with options for how to handle pronunciation variants when they occur in a corpus.

## Workshops / Tutorials

We're delighted to have participated in various workshops / conferences:
* [Annual Meeting on Phonology 2015](http://blogs.ubc.ca/amp2015/)
* [Tools for Big Data in Phonology / LabPhon 2016](http://mlmlab.org/bigphon/)
* Symposium on the role of predictability in shaping human language sound patterns / SST 2016

Example files and tutorial handouts can be downloaded from: https://github.com/PhonologicalCorpusTools/PCT_Fileshare.

## Documentation

Please see the user's manual of the latest version for complete documentation; currently available at [http://corpustools.readthedocs.org/en/latest/](http://corpustools.readthedocs.org/en/latest/). Documentation can also be found throughout the PCT software itself by clicking on "Help" (either in the main menu or in dialogue boxes relating to individual functions).

Information about how to cite PCT itself can be found at [https://corpustools.readthedocs.io/en/latest/citing_pct.html](https://corpustools.readthedocs.io/en/latest/citing_pct.html).

### About us
We are a group of researchers in the [Linguistics Department](http://linguistics.ubc.ca) at the [University of British Columbia](http://www.ubc.ca). The PI on this project is [Dr. Kathleen Currie Hall](http://linguistics.ubc.ca/persons/kathleen-hall/), and the project is supported in part by a SSHRC Insight Development grant to Dr. Hall.

### What do we mean by a "corpus"?

Within PCT, a corpus generally refers to a structured list of words, each phonologically transcribed, and accompanied by their token frequency of occurrence within some body of usage. It can contain other information as well – e.g., lexical class of the word, number of syllables, morphological parse, etc. – but it doesn’t have to. PCT can also be used to convert running text into a frequency-tagged corpus of this sort. 

### Multi-character sequences

Below, you can find lists of the multi-character sequences that are included in each of the built-in transcription-to-feature system files. You may want to use these in order to copy & paste them into the corpus creation dialogue box if you are using a corpus file that is not already delimited. See also https://github.com/PhonologicalCorpusTools/PCT_Fileshare for more detail on the transcription / feature files.

**Buckeye**: aa, aan, ae, aen, ah, ahn, ao, aon, aw, awn, ay, ayn, ch, dh, dx, eh, el, em, en, ey, eyn, hh, ih, ihn, iy, iyn, jh, ng, nx, ow, own, oy, oyn, sh, th, tq, uh, uhn, uw, uwn, zh, ehn, er, ern

**CELEX**: tS, dZ, aU, aI, eI, OI

**CMU**: TH, DH, CH, JH, SH, ZH, NG, HH, IY, IH, UH, EH, ER, AH, AH, AO, AE, AA, UW, AW, AY, EY, OW, OY, AH N, AH L

**CPA**: T/, J/, ^/, u:, A/, a/, e/, O/, o/, n,, l,

**IPA**: k̟x̟, ɡ̟ɣ̟, k̟͡x̟, ɡ̟͡ɣ̟, dʑ, tɕ, d͡ʑ, t͡ɕ, dʒ, dz, dɮ, d̠ɮ̠, tʃ, t̠ɬ̠, ts, tɬ, t̪s̪, t̪ɬ̪, d̪z̪, d̪ɮ̪, ʈʂ, ɖʐ, pf, bv, pɸ, bβ, t̪θ, d̪ð, cç, ɟʝ, kx, k̠x̠, ɡɣ, ɡ̠ɣ̠, qχ, ɢʁ, kp, ɡb, pt, bd, d͡ʒ, d͡z, d͡ɮ, d̠͡ɮ̠, t͡ʃ, t̠͡ɬ̠, t͡s, t͡ɬ, t̪͡s̪, t̪͡ɬ̪, d̪͡z̪, d̪͡ɮ̪, ʈ͡ʂ, ɖ͡ʐ, p͡f, b͡v, p͡ɸ, b͡β, t̪͡θ, d̪͡ð, c͡ç, ɟ͡ʝ, k͡x, k̠͡x̠, ɡ͡ɣ, ɡ̠͡ɣ̠, q͡χ, ɢ͡ʁ, k͡p, ɡ͡b, p͡t, b͡d, aʊ, aɪ, eɪ, oʊ, ɔɪ

**SAMPA**: I:, i:, U:, u:, E:, O:, Q:, tS, dZ, @U, aU, aI, eI, OI, n,, l,, 3`

### Functionality

* **Summary information**: Summary descriptions of a corpus, including type and token frequency of individual segments in user-defined environments.
* **Featural interpretation**: Ability to analyse a transcribed corpus with any set of phonological features; both the transcription system and the feature set may be one of the ones built-in (Hayes 2008; Mielke 2008) or may be user-defined. Phonological tiers may be extracted based on features.
* **Phonotactic probability**: Calculation of the phonotactic probability of a word, given the other words that exist in the corpus (cf. Vitevitch & Luce 2004).
* **Functional load**: Calculation of the functional load of individual pairs of sounds within the corpus, defined at either the segment or feature level (cf. Hockett 1966; Surendran & Niyogi 2003; Wedel, Kaplan, & Jackson 2013).
* **Predictability of distribution**: Calculation of the extent to which any pair of sounds is predictably distributed, given a set of environments that they can occur in (cf. Hall 2009, 2012; Hall & Hall 2013).
* **Kullback-Leibler divergence**: Calculation of the Kullback-Leibler divergence between the distributions of two sounds, again as a measure of the predictability of phonological distribution (cf. Kullback & Leibler 1951; Peperkamp et al. 2006).
* **String similarity** and **Neighbourhood density**: Calculation of the extent to which pairs of words are similar to each other using either orthographic or phonetic transcription, and calculation of neighbourhood density (cf. Frisch et al. 2004, Khorsi 2012; Greenberg & Jenkins 1964; Luce & Pisoni 1998; Yao 2011).
* **Frequency of alternation**: Estimation of the frequency with which two sounds alternate with each other, given a measure of similarity (cf. Silverman 2006, Johnson & Babel 2010, Lu 2012).
* **Informativity**: Calculation of the average information content of a given segment based on the sounds that precede it in words across the corpus (cf. Cohen-Priva 2008, 2015).
* **Mutual Information**: Calculation of the mutual information between pairs of segments in the corpus (cf. Brent 1999; Goldsmith & Riggle 2012).
* **Transitional probability**: Calculation of the transitional probability (forward or backward) between pairs of segments in the corpus (cf. Saffran 1996a, 1996b).
* **Acoustic similarity**: Calculation of the acoustic similarity between sounds / words, based on alignment of MFCCs (cf. Mielke 2012) or amplitude envelopes (cf. Lewandowski 2012), derived from .wav files.

## Standard installation (executable)

### Windows

NOTE 1: This method requires that you are running a 64-bit version of windows. You can check this by in Control Panel -> System and Security -> System.

NOTE 2: When the software is downloaded, you may get a security warning indicating that you have tried to launch an unrecognized app. Selecting "Run anyway" should allow PCT to work as expected.

Download the latest version's installer (should be a file ending in .exe) from the Phonological CorpusTools page on GitHub (https://github.com/PhonologicalCorpusTools/CorpusTools/releases). Double-click this file to install PCT to your computer. It can then be run the same as any other program, via Start -> Programs.

### Mac OS X (requires 10.8 or higher) -- PCT v 1.4.1 is confirmed to work on 10.13 and higher, but may have issues on earlier OS platforms

NOTE 1: When the software is downloaded, you may get a security warning indicating that you have tried to launch an unrecognized app. If you Ctrl-click on the application and select "Open," you should be able to override the security warning and use PCT normally.

Download the latest version's installer (should be a file ending in .dmg) from the Phonological CorpusTools page on GitHub (https://github.com/PhonologicalCorpusTools/CorpusTools/releases). You can then double-click this file to run Phonological CorpusTools. You can move the icon to your toolbar like any other application.

### Linux

There is currently no executable option available for Linux operating systems. Please use the fallback installation method below to install from source.


## Fallback installation (setup.py)

### Windows, Mac OS X, or Linux

Dependencies:
- Python 3.3 or higher: https://www.python.org/downloads/release/python-341/
- Setuptools: https://pypi.python.org/pypi/setuptools
- PyQt5: http://www.riverbankcomputing.com/software/pyqt/download5
- TextGrid: https://github.com/kylebgorman/textgrid

If you expect to use the acoustic similarity module, there are additional dependencies:
- NumPy: http://www.numpy.org/
- SciPy: http://www.scipy.org/
(If you are on Windows and can't successfully use the acoustic similarity module after installing from the above sources, you may want to try installing from the precompiled binaries here: http://www.lfd.uci.edu/~gohlke/pythonlibs/ .)

Download the latest version of the source code for Phonological CorpusTools from the GitHub page (https://github.com/PhonologicalCorpusTools/CorpusTools/releases). After expanding the file, you will find a file called 'setup.py' in the top level directory. Run it in *one* of the following ways:

1. Double-click it. If this doesn't work, access the file properties and ensure that you have permission to run the file; if not, give them to yourself. In Windows, this may require that you open the file in Administrator mode (also accessible through file properties). If your computer opens the .py file in a text editor rather than running it, you can access the file properties to set Python 3.x as the default program to use with run .py files. If the file is opened in IDLE (a Python editor), you can use the "Run" button in the IDLE interface to run the script instead.

2. Open a terminal window and run the file. In Linux or Mac OS X, there should be a Terminal application pre-installed. In Windows, you may need to install Cygwin ( https://www.cygwin.com/ ). Once the terminal window is open, nagivate to the top level CorpusTools folder---the one that has setup.py in it. (Use the command 'cd' to navigate your filesystem; Google "terminal change directory" for further instructions.) Once in the correct directory, run this command: "python3 setup.py install" (no quotes). You may lack proper permissions to run this file, in which case on Linux or Mac OS X you can instead run "sudo python3 setup.py install". If Python 3.x is the only version of Python on your system, it may be possible or necessary to use the command "python" rather than "python3".

Phonological CorpusTools should now be installed! Run it from a terminal window using the command "pct". You can also open a "Run" dialogue and use the command "pct" there. In Windows, the Run tool is usuall found in All Programs -> Accessories.

## References
* Archangeli, Diana & Douglas Pulleyblank. 2013. The role of UG in phonology. Proceedings of the West Coast Conference on Formal Linguistics 31. Somerville, MA: Cascadilla Press.
* Brent, Michael R. 1999. An efficient, probabilistically sound algorithm for segmentation and word discovery. Machine Learning 34.71-105.
* Brysbaert, Marc, & Boris New. 2009. Moving beyond Kučera and Francis: A critical evaluation of current word frequency norms and the introduction of a new and improved word frequency measure for American English. Behavior Research Methods 41(4): 977-990.
* Bybee, Joan L. 2001. Phonology and language use. Cambridge: Cambridge UP.
* Cohen Priva, Uriel. 2008. Using information content to predict phone deletion. In N. Abner & J. Bishop (eds.), Proceedings of the 27th West Coast Conference on Formal Linguistics, 90-98. Somerville, MA: Cascadilla Proceedings Project.
* Cohen Priva, Uriel. 2015. Informativity affects consonant duration and deletion rates. Laboratory Phonology 6(2). 243-278. 
* Ernestus, Mirjam. 2011. Gradience and categoricality in phonological theory. In The Blackwell Companion to Phonology, ed. by M. van Oostendorp, C.J. Ewen, E. Hume & K. Rice, 2115-36. Oxford: Wiley-Blackwell.
* Chomsky, Noam & Morris Halle. 1968. The sound pattern of English. New York: Harper & Row.
* Frisch, Stefan A. 2011. Frequency effects. In The Blackwell Companion to Phonology, ed. by M. van Oostendorp, C.J. Ewen, E. Hume & K. Rice, 2137-63. Oxford: Wiley-Blackwell.
* Frisch, Stefan, Janet B. Pierrehumbert & Michael B. Broe. 2004. Similarity avoidance and the OCP. Natural Language and Linguistic Theory 22.179-228.
* Goldsmith, John & Jason Riggle. 2012. Information theoretic approaches to phonological structure: the case of Finnish vowel harmony. Natural Language and Linguistic Theory 30.859-96.
* Greenberg, J.H. & J. Jenkins. 1964. Studies in the psychological correlated of the sound system of American English. Word 20.157-77.
* Hall, Kathleen Currie. 2009. A probabilistic model of phonological relationships from contrast to allophony. Columbus, OH: The Ohio State University Doctoral dissertation.
* Hall, Kathleen Currie. 2012. Phonological relationships: A probabilistic model. McGill Working Papers in Linguistics 22.
* Hall, Daniel Currie & Kathleen Currie Hall. 2013. Marginal contrasts and the Contrastivist Hypothesis. Paper presented to the Linguistics Association of Great Britain, London, 2013.
* Hayes, Bruce. 2009. Introductory Phonology. Malden, MA: Blackwell - Wiley.
* Hockett, Charles F. 1966. The quantification of functional load: A linguistic problem. U.S. Air Force Memorandum RM-5168-PR.
* Hume, Elizabeth, Kathleen Currie Hall & Andrew Wedel. to appear. Strategic responses to uncertainty: Strong and weak sound patterns. Proceedings of the 5th International Conference on Phonology and Morphology. Korea.
* Johnson, Keith, & Molly Babel. 2010. On the perceptual basis of distinctive features: Evidence from the perception of fricatives by Dutch and English speakers. Journal of Phonetics 38: 127-136.
* Khorsi, Ahmed. 2012. On morphological relatedness. Natural Language Engineering.1-19.
* Kullback, Solomon & Richard A. Leibler. 1951. On information and sufficiency. Annals of Mathematical Statistics 22.79-86.
* Lewandoski, Natalie. 2012. Talent in nonnative phonetic convergence: Universität Stuttgart Doctoral dissertation.
* Lu, Yu-an. 2012. The role of alternation in phonological relationships: Stony Brook University Doctoral dissertation.
* Luce, Paul A. & David B. Pisoni. 1998. Recognizing spoken words: The neighborhood activation model. Ear Hear 19.1-36.
* Mielke, Jeff. 2008. The emergence of distinctive features. Oxford: Oxford UP.
* Mielke, J. 2012. A phonetically based metric of sound similarity. Lingua, 122(2), 145-163. 
* Peperkamp, Sharon, Le Calvez, Rozenn, Nadal, Jean-Pierre, & Dupoux, Emmanuel. (2006). The acquisition of allophonic rules: Statistical learning with linguistic constraints. Cognition, 101, B31-B41.
* Saffran, Jenny R., Aslin, Richard N., and Newport, Elisa L. (1996a). Statistical learning by 8-month-old infants. Science, 274:1926–1928.
* Saffran, Jenny R., Newport, Elisa L., and Aslin, Richard N. (1996b). Word segmentation: The role of distributional cues. Journal of Memory and Languages, 35:606–621.
* Silverman, Daniel. 2006. A critical introduction to phonology: Of sound, mind, and body. London/New York: Continuum.
* Surendran, Dinoj & Partha Niyogi. 2003. Measuring the functional load of phonological contrasts. In Tech. Rep. No. TR-2003-12. Chicago.
* Vaden, K. I., H. R. Halpin & G. S. Hickok. 2009. Irvine Phonotactic Online Dictionary, Version 2.0. [Data file.] Available from: http://www.iphod.com.
* Vitevitch, Michael S. & Luce, Paul A. (2004). A web-based interface to calculate phonotactic probability for words and nonwords in English. Behavior Research Methods, Instruments, and Computers, 36(3), 481-487. https://doi.org/10.3758/bf03195594 
* Wedel, Andrew, Abby Kaplan & Scott Jackson. 2013. High functional load inhibits phonological contrast loss: A corpus study. Cognition 128.179-86.
* Weide, Robert L. 1994. CMU Pronouncing Dictionary. http://www.speech.cs.cmu.edu/cgi-bin/cmudict.
* Yao, Yao. 2011. The effects of phonological neighborhoods on pronunciation variation in conversational speech. Berkeley: University of California, Berkeley Doctoral dissertation. 
