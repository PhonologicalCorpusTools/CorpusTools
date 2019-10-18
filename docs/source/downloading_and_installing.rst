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
fastest way to get PCT up and running on your machine. Note: PCT v 1.4.1 is confirmed to work on Mac OS 10.13 and higher, but may have issues on earlier OS platforms

Download
========

#. Go to the `PCT releases page`_.
#. Click on the link for your operating system with the highest number (= most recent version).
 

Windows Installer
=================

# NOTE 1: This method requires that you are running a 64-bit version of windows. You can check this by in Control Panel -> System and Security -> System.

# NOTE 2: When the software is downloaded, you may get a security warning indicating that you have tried to launch an unrecognized app. Selecting "Run anyway" should allow PCT to work as expected.

# Download the latest version's installer (should be a file ending in .exe) from the Phonological CorpusTools page on GitHub (https://github.com/PhonologicalCorpusTools/CorpusTools/releases). Double-click this file to install PCT to your computer. It can then be run the same as any other program, via Start -> Programs.


Mac Executable -- PCT v 1.4.1 is confirmed to work on 10.13 and higher, but may have issues on earlier OS platforms
==============

# NOTE 1: When the software is downloaded, you may get a security warning indicating that you have tried to launch an unrecognized app. If you Ctrl-click on the application and select "Open," you should be able to override the security warning and use PCT normally.

# Download the latest version's installer (should be a file ending in .dmg) from the Phonological CorpusTools page on GitHub (https://github.com/PhonologicalCorpusTools/CorpusTools/releases). You can then double-click this file to run Phonological CorpusTools. You can move the icon to your toolbar like any other application.


Linux / Fallback instructions
=============================

1. Dependencies: You’ll first need to make sure all of the following
   are installed. The third and fourth ones (NumPy and SciPy) are
   needed only for the Acoustic Similarity functionality to work.

  a. `Python 3.3 or higher <https://www.python.org/downloads/release/python-341/>`_
  b. `NumPy <http://www.numpy.org/>`_
  c. `SciPy <http://www.scipy.org/>`_
  d. (NB: If you are on Windows and can't successfully use the acoustic
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
