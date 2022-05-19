import sys
import os
import scipy.special
import PyQt5
from cx_Freeze import setup, Executable

def readme():
    with open('README.md') as f:
        return f.read()

ufuncs_path = scipy.special._ufuncs.__file__
incl_files = [(ufuncs_path,os.path.split(ufuncs_path)[1]),('docs','html')]

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    libegl = os.path.join(os.path.dirname(PyQt5.__file__),'libEGL.dll')
    incl_files.append((libegl,os.path.split(libegl)[1]))

group_name = 'PCT'

exe_name = 'Phonological CorpusTools'

shortcut_table = [
    ("StartMenuShortcut",       # Shortcut
     "ProgramMenuFolder",       # Directory_
     "%s" % (exe_name,),        # Name
     "TARGETDIR",               # Component_
     "[TARGETDIR]pct.exe",      # Target
     None,                      # Arguments
     None,                      # Description
     None,                      # Hotkey
     None,                      # Icon
     None,                      # IconIndex
     None,                      # ShowCmd
     'TARGETDIR'                # WkDir
     )
    ]

build_exe_options = {"excludes": [
                        'matplotlib',
                        "tcl",
                        'ttk',
                        "tkinter",],
                    "include_files":incl_files,
                    "includes": [
                            "PyQt5",
                            "PyQt5.QtWebKitWidgets",
                            #"PyQt5.QtWebKit",
                            #"PyQt5.QtWebEngineWidgets",
                            #"PyQt5.QtPrintSupport",
                            "PyQt5.QtMultimedia",
                            "numpy",
                            "scipy",
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
                            "scipy.spatial",
                            "textgrid",
                            "sys",
                            "multiprocessing"]
                            }

msi_data = {"Shortcut": shortcut_table}

bdist_msi_options = {
        'upgrade_code':'{9f3fd2c0-db11-4d9b-8124-2e91e6cfd19d}',
        'add_to_path': False,
        'initial_target_dir': r'[ProgramFiles64Folder]\%s\%s' % (group_name, exe_name),
        'data':msi_data}

bdist_mac_options = {'iconfile':'docs/images/icon.icns',
                    'qt_menu_nib':'/opt/local/share/qt5/plugins/platforms',
                    'bundle_name':'Phonological CorpusTools',
                    #'include_frameworks':["/Library/Frameworks/Tcl.framework",
                    #                    "/Library/Frameworks/Tk.framework"]
                                        }
bdist_dmg_options = {'applications_shortcut':True}

setup(name='Phonological CorpusTools',
      version='1.5.1',
      description='',
      long_description='',
      classifiers=[
        #'Development Status :: 3 - Alpha',
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
                'corpustools.acousticsim',
                'corpustools.corpus',
                'corpustools.corpus.classes',
                'corpustools.corpus.io',
                'corpustools.freqalt',
                'corpustools.funcload',
                'corpustools.kl',
                'corpustools.prod',
                'corpustools.phonosearch',
                'corpustools.gui',
                'corpustools.symbolsim',
                'corpustools.neighdens',
                'corpustools.mutualinfo',
                'corpustools.phonoprob',
                'corpustools.informativity'
                #'scipy'
                ],
      executables = [Executable('corpustools/command_line/pct.py',
                            #targetName = 'pct',
                            base=base,
                            #shortcutDir=r'[StartMenuFolder]\%s' % group_name,
                            #shortcutName=exe_name,
                            icon='corpustools/command_line/favicon.png'
                            )],
      options={
          'bdist_msi': bdist_msi_options,
          'build_exe': build_exe_options,
          'bdist_mac':bdist_mac_options,
          'bdist_dmg':bdist_dmg_options}
      )
