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

Download the latest executable (`.exe`) file from the Phonological CorpusTools
[release page](https://github.com/PhonologicalCorpusTools/CorpusTools/releases).
Double-click this file to run PCT.

### Mac OS X

Download the .dmg for the latest release (e.g. Phonological.CorpusTools-<version>.dmg 
from the Phonological CorpusTools [releases page](https://github.com/PhonologicalCorpusTools/CorpusTools/releases).
Install Phonological CorpusTools by dragging the app into the Applications
directory.

### Linux

There is currently no executable option available for Linux operating systems.
Please use the fallback installation method below to install from source.


## Fallback installation

### Windows, Mac OS X, or Linux

1. Install Python 3.3 or higher (Python 3.10 recommended) if your system does not have Python: https://www.python.org/downloads/ 

2. Download the latest source code for Phonological CorpusTools by clicking on `Code` > `` (see image below).
   ![image](https://github.com/user-attachments/assets/b4bf61c6-87e9-4830-b396-0dc7cc1783bc)
   
   If you want to download a specific version, go to [releases page](https://github.com/PhonologicalCorpusTools/CorpusTools/releases)
   and Download `Source code (zip)` or `Source code (tar.gz)` under `Assets`.


4. Unpack the source code in a directory of your choice. 

5. Open a terminal (or command prompt for Windows) and `cd` into the directory.

6. Use the following command to install the dependencies
   ```bash
   pip install -r requirements.txt
   ```
   
### Windows and Mac OS X
6. Once all dependencies are installed, run this command to create an executable.
   ```bash
   pyinstaller pct.spec
   ```
7. Now you should be able to run PCT using the icon in the `dist` directory.

### Linux
6. Once all dependencies are installed, run this command to run PCT from the source code.
   ```bash
   python ./bin/pct_qt_debug.py
   ```
