from esky import bdist_esky
from distutils.core import setup
import scipy.special
import PyQt5
import os
import sys
from glob import glob


ufuncs_path = scipy.special._ufuncs.__file__
doc_files = dict()
for root, dirnames, filenames in os.walk('docs\build'):
    if os.path.basename(root).startswith('.'):
        continue
    if os.path.basename(root) in ['_images', '_sources']:
        continue
    hr = root.replace('docs\build', 'html')
    if hr not in doc_files:
        doc_files[hr] = list()
    for f in filenames:
        if not f.startswith('.'):
            doc_files[hr].append(os.path.join(root,f))

incl_files = list(doc_files.items())
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    libegl = os.path.join(os.path.dirname(PyQt5.__file__),'libEGL.dll')
    #incl_files.append((libegl,os.path.split(libegl)[1]))

group_name = 'PCT'

exe_name = 'Phonological CorpusTools'

exe = bdist_esky.Executable('corpustools/command_line/pct.py',
                            #targetName = 'pct',
                            gui_only=True,
                            #shortcutDir=r'[StartMenuFolder]\%s' % group_name,
                            #shortcutName=exe_name,
                            icon='docs/images/icon.icns'
                            )

build_exe_options = {"excludes": [
                        'corpustools.acousticsim.tests',
                        'corpustools.corpus.tests',
                        'corpustools.funcload.tests',
                        'corpustools.prod.tests',
                        'matplotlib',
                        "tcl",
                        'ttk',
                        "tkinter",],
                    "includes": [
                            "PyQt5",
                            "PyQt5.QtWebKitWidgets",
                            "PyQt5.QtWebKit",
                            "PyQt5.QtPrintSupport",
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
                            "acousticsim",
                            "sys"]
                            }

bdist_mac_options = {'iconfile':'docs/images/icon.icns',
                    'qt_menu_nib':'/opt/local/share/qt5/plugins/platforms',
                    'bundle_name':'Phonological CorpusTools',
                    #'include_frameworks':["/Library/Frameworks/Tcl.framework",
                    #                    "/Library/Frameworks/Tk.framework"]
                                        }
bdist_dmg_options = {'applications_shortcut':True}

setup(name="Phonological CorpusTools",
        version="1.0.1",
        scripts=[exe],
        packages=['corpustools',
                'corpustools.corpus',
                'corpustools.corpus.io',
                'corpustools.corpus.classes',
                'corpustools.freqalt',
                'corpustools.funcload',
                'corpustools.kl',
                'corpustools.prod',
                'corpustools.gui',
                #'corpustools.acousticsim',
                'corpustools.symbolsim',
                'corpustools.neighdens'],
        data_files = incl_files,
        options={"bdist_esky":{
                "freezer_module":"cxfreeze",
                "freezer_options":{
                "includes":[
                            "PyQt5",
                            "PyQt5.QtWebKitWidgets",
                            "PyQt5.QtWebKit",
                            "PyQt5.QtPrintSupport",
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
                            "acousticsim",
                            "sys"],
                "excludes":[
                        'corpustools.acousticsim.tests',
                        'corpustools.corpus.tests',
                        'corpustools.funcload.tests',
                        'corpustools.prod.tests',
                        'matplotlib',
                        "tcl",
                        'ttk',
                        "tkinter"]
                }
                }
                            },
     )
