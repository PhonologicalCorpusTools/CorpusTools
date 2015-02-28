from esky import bdist_esky
from distutils.core import setup
import scipy.special
import PyQt5
import os
import sys
from glob import glob

freezer_module = "cxfreeze"

ufuncs_path = scipy.special._ufuncs.__file__
doc_files = dict()
for root, dirnames, filenames in os.walk('docs/build'):
    if os.path.basename(root).startswith('.'):
        continue
    if os.path.basename(root) in ['_images', '_sources']:
        continue
    hr = root.replace('docs/build', 'html')
    if hr not in doc_files:
        doc_files[hr] = list()
    for f in filenames:
        if not f.startswith('.'):
            doc_files[hr].append(os.path.join(root,f))

incl_files = list(doc_files.items()) #+ [('docs/images','docs/images/icon.icns')]
scripts = ['corpustools/command_line/pct.py']
base = None

freezer_options = {
                "includes":[
                            "sip",
                            "PyQt5",
                            "PyQt5.QtWebKitWidgets",
                            "PyQt5.QtWebKit",
                            "PyQt5.QtPrintSupport",
                            "PyQt5.QtMultimedia",
                            "esky",
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
                
if sys.platform == "win32":
    base = "Win32GUI"
    libegl = os.path.join(os.path.dirname(PyQt5.__file__),'libEGL.dll')
    #incl_files.append((libegl,os.path.split(libegl)[1])
elif sys.platform == 'darwin':
    from setuptools import setup
    freezer_module = 'py2app'
    extra_opts  = {
        'plist':{
            'LSUIElement':True,
            'CFBundleName':'PhonologicalCorpusTools',
            'CFBundleDisplayName':'Phonological CorpusTools',
            'NSUserNotificationAlertStyle': 'alert'
            },
        'app': scripts,
        'argv_emulation': False,
        'data_files':incl_files,
        'scripts': scripts,
        'iconfile':'docs/images/icon.icns'
        }
    freezer_options.update(extra_opts)

group_name = 'PCT'

exe_name = 'Phonological CorpusTools'

exe = bdist_esky.Executable('corpustools/command_line/pct.py',
                            #targetName = 'pct',
                            gui_only=True,
                            #shortcutDir=r'[StartMenuFolder]\%s' % group_name,
                            #shortcutName=exe_name,
                            #icon='docs/images/icon.icns'
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
                            "sip",
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

def fix_freeze(self):
    import shutil
    files_for_copying = ['libbz2.1.0.6.dylib','libbz2.1.0.dylib',
                         'libcrypto.1.0.0.dylib','libgcc_s.1.dylib',
                         'libgfortran.3.dylib',
                         'libglib-2.0.0.dylib','libgthread-2.0.0.dylib',
                         'libiconv.2.dylib','libicudata.54.1.dylib',
                         'libicudata.54.dylib','libicui18n.54.1.dylib',
                         'libicui18n.54.dylib','libicuuc.54.1.dylib',
                         'libicuuc.54.dylib','libintl.8.dylib',
                         'libjpeg.9.dylib','liblzma.5.dylib',
                         'libncurses.5.dylib','libpcre16.0.dylib',
                         'libpng16.16.dylib','libquadmath.0.dylib',
                         'libssl.1.0.0.dylib','libz.1.2.8.dylib',
                         'libz.1.dylib']
    name = 'PhonologicalCorpusTools-1.0.1.macosx-10_9-x86_64'
    for f in files_for_copying:
        src = os.path.join('dist',name,name,'PhonologicalCorpusTools.app','Contents','Frameworks',f)
        dst = os.path.join('dist',name,'Contents','Frameworks',f)
        shutil.copyfile(src,dst)
    print(os.getcwd())
    print(os.path.exists('build/PhonologicalCorpusTools.app'))
    #src = os.path.join('build','PhonologicalCorpusTools.app')
    dst = os.path.join('dist',name,name, 'PhonologicalCorpusTools.app')
    open(os.path.join(dst,'Content','Resources','qt.conf'),'w').close()
    #shutil.rmtree(dst)
    #shutil.copytree(src, dst)
    t
    print(self)

setup(name="PhonologicalCorpusTools",
        version="1.0.1",
        scripts=[exe],
        packages=['corpustools',
                'corpustools.acousticsim',
                'corpustools.corpus',
                'corpustools.corpus.classes',
                'corpustools.corpus.io',
                'corpustools.freqalt',
                'corpustools.funcload',
                'corpustools.kl',
                'corpustools.prod',
                'corpustools.gui',
                'corpustools.symbolsim',
                'corpustools.neighdens',
                'corpustools.mutualinfo',
                'corpustools.phonoprob',
                'corpustools.command_line'],
        data_files = incl_files,
        options={
                #"bdist_mac_options":bdist_mac_options,
                "bdist_esky":{
                "pre_zip_callback":fix_freeze,
                "freezer_module":freezer_module,
                "freezer_options":freezer_options
                            },
                }
     )
