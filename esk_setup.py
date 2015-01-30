from esky import bdist_esky
from distutils.core import setup

setup(name="appname",
      version="1.2.3",
      scripts=["appname/script1.py","appname/gui/script2.pyw"],
      options={"bdist_esky":{
                "freezer_module":"cxfreeze",
                "includes":["numpy",
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

                            },
     )
