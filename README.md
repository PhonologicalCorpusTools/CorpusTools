Phonological CorpusTools
========================

[![Build Status](https://travis-ci.org/PhonologicalCorpusTools/CorpusTools.svg?branch=master)](https://travis-ci.org/PhonologicalCorpusTools/CorpusTools?branch=master)
[![Coverage Status](https://coveralls.io/repos/PhonologicalCorpusTools/CorpusTools/badge.svg?branch=master)](https://coveralls.io/r/PhonologicalCorpusTools/CorpusTools?branch=master)

[![Documentation Status](https://readthedocs.org/projects/corpustools/badge/?version=latest)](https://readthedocs.org/projects/corpustools/?badge=latest)

This document contains installation instructions for Phonological
CorpusTools (PCT). For a description of available functionality, please
refer to the documentation available on ReadTheDocs
(http://corpustools.readthedocs.org/en/master/).


## Standard installation (executable)

### Windows

(NOTE: This method requires that you are running a 64-bit version of
windows. You can check this by in Control Panel -> System and
Security -> System.)

Download the latest version's installer from the Phonological CorpusTools
release page (https://github.com/PhonologicalCorpusTools/CorpusTools/releases).
Double-click this file to install PCT to your computer. It can then be
run the same as any other program, via Start -> Programs.

### Mac OS X

Download the file 'Phonological.CorpusTools-1.1.0.dmg' from the
Phonological CorpusTools releases page
(https://github.com/PhonologicalCorpusTools/CorpusTools/releases).
Install Phonological CorpusTools by dragging the app into the Applications
directory.

### Linux

There is currently no executable option available for Linux operating systems.
Please use the fallback installation method below to install from source.


## Fallback installation (setup.py)

### Windows, Mac OS X, or Linux

Dependencies:
- Python 3.3 or higher: https://www.python.org/downloads/
- Setuptools: https://pypi.python.org/pypi/setuptools
- PyQt5: http://www.riverbankcomputing.com/software/pyqt/download5

If you expect to use the acoustic similarity module, there are additional
dependencies:
- NumPy: http://www.numpy.org/
- SciPy: http://www.scipy.org/
(If you are on Windows and can't successfully use the acoustic similarity
module after installing from the above sources, you may want to try
installing from the precompiled binaries here:
http://www.lfd.uci.edu/~gohlke/pythonlibs/ .)

Download the latest version of the source code for Phonological CorpusTools
from the releases page (https://github.com/PhonologicalCorpusTools/CorpusTools/releases).
After expanding the file, you will find a file called 'setup.py' in the top
level directory. Run it in *one* of the following ways:

1. Double-click it. If this doesn't work, access the file properties and
   ensure that you have permission to run the file; if not, give them to
   yourself. In Windows, this may require that you open the file in
   Administrator mode (also accessible through file properties).
   If your computer opens the .py file in a text editor rather than
   running it, you can access the file properties to set Python 3.x
   as the default program to use with run .py files. If the file is
   opened in IDLE (a Python editor), you can use the "Run" button in
   the IDLE interface to run the script instead.

2. Open a terminal window and run the file. In Linux or Mac OS X, there
   should be a Terminal application pre-installed. In Windows, you may
   need to install Cygwin ( https://www.cygwin.com/ ). Once the terminal
   window is open, nagivate to the top level CorpusTools folder---the
   one that has setup.py in it. (Use the command 'cd' to navigate your
   filesystem; Google "terminal change directory" for further instructions.)
   Once in the correct directory, run this command: `python3 setup.py install`.
   You may lack proper permissions to run this file, in
   which case on Linux or Mac OS X you can instead run `sudo python3 setup.py install`.
   If Python 3.x is the only version of Python on your system, it may be
   possible or necessary to use the command `python` rather than `python3`.

Phonological CorpusTools should now be installed! Run it from a terminal
window using the command `pct`. You can also open a "Run" dialogue and
use the command `pct` there. In Windows, the Run tool is usuall found in
All Programs -> Accessories.
