.. _downloading_and_installing:

**************************
Downloading and installing
**************************

.. _PCT website: http://phonologicalcorpustools.github.io/CorpusTools/

.. _GitHub repository: https://github.com/PhonologicalCorpusTools/CorpusTools/

.. _kathleen.hall@ubc.ca: kathleen.hall@ubc.ca

.. _PCT releases page: https://github.com/PhonologicalCorpusTools/CorpusTools/releases

PCT is currently available for Mac, PC, and Linux machines.
It can be downloaded from `PCT releases page`_
using the following steps. Note that there are several dependencies that are
pre-requisites before PCT can function properly. For Mac and Windows machines,
we have created executable files that bundle most of the dependencies and the
PCT software itself into a single package. Using these is the easiest /
fastest way to get PCT up and running on your machine. Note: PCT v 1.4.1 is confirmed to work on Mac OS 10.13 and higher, but may have issues on earlier OS platforms.

Download
========

#. Go to the `PCT releases page`_.
#. Click on the link for your operating system with the highest number (= most recent version).
 

Windows Executable
------------------

# NOTE 1: This method requires that you are running a 64-bit version of windows. You can check this by in Control Panel -> System and Security -> System.

# NOTE 2: When the software is downloaded, you may get a security warning indicating that you have tried to launch an unrecognized app. Selecting "Run anyway" should allow PCT to work as expected.

# Download the latest version's executable (should be a file ending in .exe) from the Phonological CorpusTools page on GitHub (https://github.com/PhonologicalCorpusTools/CorpusTools/releases). Double-click this file to run PCT to your computer. It can then be run the same as any other program.


Mac Executable -- PCT v 1.4.1 is confirmed to work on 10.13 and higher, but may have issues on earlier OS platforms
--------------

# NOTE 1: When the software is downloaded, you may get a security warning indicating that you have tried to launch an unrecognized app. If you Ctrl-click on the application and select "Open," you should be able to override the security warning and use PCT normally.

# NOTE 2: Similarly, you may get a warning asking whether you want to give PCT access to your Documents folder. In order for PCT to function properly, you should grant this permission. See details in :ref:`local_storage`. If you do not give permission when first downloading PCT, the software will still download and create sub-folders in your Documents folder, but the program itself will not launch. To change your permissions at any point, you can go to System Preferences / Security and Privacy / Privacy / Files and Folders, and then specify that Phonological CorpusTools can have access to the Documents folder.

# Download the latest version's installer (should be a file ending in .dmg) from the Phonological CorpusTools page on GitHub (https://github.com/PhonologicalCorpusTools/CorpusTools/releases). You can then double-click this file to run Phonological CorpusTools. You can move the icon to your toolbar like any other application.


Linux / Fallback instructions
=============================

1. Dependencies: You’ll first need to make sure all of the following
   are installed. The third and fourth ones (NumPy and SciPy) are
   needed only for the Acoustic Similarity functionality to work.

  a. `Python 3.3 or higher <https://www.python.org/downloads/release/python-341/>`_
  b. `Regex <https://pypi.org/project/regex/>`_
  c. `NumPy <http://www.numpy.org/>`_
  d. `SciPy <http://www.scipy.org/>`_
  e. `Scikit-learn <https://scikit-learn.org/stable/install.html>`_
  f. (NB: If you are on Windows and can't successfully use the acoustic
     similarity module after installing NumPy and SciPy from the above sources,
     you may want to try installing them from `precompiled binaries
     <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_.)

2. Get the source code for PCT. Click on either the .zip or the .gz file
   on the `PCT releases page`_ or the `GitHub repository`_,
   to download the zipped or tarball version of the code, depending
   on your preference.

3. After expanding the file, you will find a file called ``setup.py``
   in the top level directory. Run it in one of the following ways:

  a. Double-click it. If this doesn't work, access the file properties
     and ensure that you have permission to run the file; if not,
     give them to yourself. In Windows, this may require that you
     open the file in Administrator mode (also accessible through
     file properties). If your computer opens the .py file in a text
     editor rather than running it, you can access the file properties
     to set Python 3.x as the default program to use with run .py files.
     If the file is opened in IDLE (a Python editor), you can use the
     "Run" button in the IDLE interface to run the script instead.
  b. Open a terminal window and run the file. In Linux or Mac OS X,
     there should be a Terminal application pre-installed. In Windows,
     you may need to install `Cygwin <https://www.cygwin.com/>`_. Once
     the terminal window is open, nagivate to the top level CorpusTools
     folder---the one that has setup.py in it. (Use the command 'cd'
     to navigate your filesystem; Google "terminal change directory" for
     further instructions.) Once in the correct directory, run this
     command: ``python3 setup.py install``. You may lack proper
     permissions to run this file, in which case on Linux or Mac OS X
     you can instead run ``sudo python3 setup.py install``. If Python 3.x
     is the only version of Python on your system, it may be possible or
     necessary to use the command ``python`` rather than ``python3``.

4. Phonological CorpusTools should now be installed! Run it from a
   terminal window using the command ``pct``. You can also open a
   "Run" dialogue and use the command ``pct`` there. In Windows, the
   Run tool is usually found in All Programs -> Accessories.

.. _local_storage:

Local storage
=============
When using PCT, certain special (PCT-specific) files are created. These include .corpus files (for PCT's storage of your corpora), .feature files (for storage of your transcription-to-feature files), .searches files (for storing saved search paramaters), and various .txt files (usually for listing specific results or errors that PCT encounters). 


Once PCT creates or downloads these files, they are saved in your local hard drive for later use. Be default, your PCT working directory is either
“C:\\Users\\[USER NAME]\\Documents\\PCT\\CorpusTools\\” (for Windows machines), or “~/Documents/PCT/CorpusTools/” (for macOS or Linux machines).
You will find several directories in this directory:

   * “CORPUS” is the place for the corpus files you created or downloaded (cf. :ref:`loading_corpora`).
   * “ERRORS” is where you can find error messages for the environment exhaustivity (cf. :ref:`predictability_of_distribution`).
   * “FEATURE” is the folder where all your feature files are saved (cf. :ref:`transcriptions_and_feature_systems`).
   * “SEARCH” is where you can find recent phonological searches (recent.searches) and saved searches (saved.searches). See :ref:`saving_phono_search` for how to save a search.

Occasionally, it is useful to access these folders directly. For example, if you want to give your corpus or feature files to another user, or access them on a different maching, you can copy the files to the relevant path in the new
machine. Similarly, if you have received a file that runs with PCT (e.g. a corpus file from the developers), you will need to save it in the correct directory for PCT to recognize it. You can also directly download the built-in .corpus and .feature files from https://github.com/PhonologicalCorpusTools/PCT_Fileshare.
Please note that the working directory will not exist if you have never run PCT.

See :ref:`preferences` for information on how to change the working directory.
