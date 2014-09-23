

import sys
from cx_Freeze import setup, Executable

def readme():
    with open('README.md') as f:
        return f.read()

group_name = 'PCT'

exe_name = 'Phonological CorpusTools'

shortcut_table = [
    ("StartMenuShortcut",        # Shortcut
     "ProgramMenuFolder",          # Directory_
     "%s" % (exe_name,),           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]pct.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,   # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

build_exe_options = {"excludes": [
                        'corpustools.acousticsim.tests',
                        'corpustools.corpus.tests',
                        'corpustools.funcload.tests',
                        'corpustools.prod.tests',
                        'matplotlib'],
                    "includes": [
                            "tkinter",
                            "numpy.lib.format",
                            "numpy.linalg",
                            "numpy.linalg._umath_linalg",
                            "numpy.linalg.lapack_lite",
                            "scipy.io.matlab.streams",
                            "scipy.integrate",
                            "scipy.integrate.vode",
                            #"scipy.sparse.linalg.dsolve.umfpack",
                            "scipy.integrate.lsoda",
                            "scipy.special",
                            "scipy.special._ufuncs_cxx",
                            "scipy.sparse.csgraph._validation",
                            "sys"],
                            #'icon':'./resources/logo.ico'
                            }

msi_data = {"Shortcut": shortcut_table}

bdist_msi_options = {
        'upgrade_code':'{9f3fd2c0-db11-4d9b-8124-2e91e6cfd19d}',
        'add_to_path': False,
        'initial_target_dir': r'[ProgramFiles64Folder]\%s\%s' % (group_name, exe_name),
        'data':msi_data}

bdist_mac_options = {#'iconfile':'./resources/logo.ico',
                    'bundle_name':'Phonological CorpusTools',
                    #'include_frameworks':["/Library/Frameworks/Tcl.framework",
                    #                    "/Library/Frameworks/Tk.framework"]
                                        }

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name='Phonological CorpusTools',
      version='0.15.1',
      description='',
      long_description='',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='phonology corpus phonetics',
      url='https://github.com/kchall/CorpusTools',
      author='PCT',
      author_email='kathleen.hall@ubc.ca',
      packages=['corpustools',
                'corpustools.corpus',
                'corpustools.freqalt',
                'corpustools.funcload',
                'corpustools.prod',
                'corpustools.gui',
                'corpustools.acousticsim',
                'corpustools.symbolsim'],
      executables = [Executable('bin/pct.py',
                            #targetName = 'PhonologicalCorpusTools',
                            base=base,
                            #shortcutDir=r'[StartMenuFolder]\%s' % group_name,
                            #shortcutName=exe_name,
                            #icon='docs/images/logo.ico'
                            )],
      options={
          'bdist_msi': bdist_msi_options,
          'build_exe': build_exe_options,
          'bdist_mac':bdist_mac_options}
      )
