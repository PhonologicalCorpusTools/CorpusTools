
import sys
from cx_Freeze import setup, Executable

def readme():
    with open('README.md') as f:
        return f.read()
        
build_exe_options = {"excludes": ['scipy.signal','scipy.io',
                                    'scipy.io.matlab',
                                    'scipy.io.matlab.mio_utils',
                                    'scipy.io.matlab.mio5_utils',
                                    'scipy.io.matlab.streams','scipy.spatial.distance',
                                    'numpy','numpy.fft',
                                    'corpustools.acousticsim',
                                    'corpustools.acousticsim.tests']}
        
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name='corpustools',
      version='0.15',
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
      author='Phonological Corpus Tools',
      author_email='kathleen.hall@ubc.ca',
      packages=['corpustools', 
                'corpustools.acousticsim',
                'corpustools.acousticsim.tests',
                'corpustools.corpus',
                'corpustools.freqalt',
                'corpustools.funcload',
                'corpustools.prod',
                'corpustools.gui',
                'corpustools.symbolsim'],
      #install_requires=[
      #    'pillow',
          #'numpy',
          #'scipy'
      #],
      entry_points = {
        'console_scripts': ['pct=corpustools.pct:main'],
    },
    console=['bin/pct.py'],
      executables = [Executable('bin/pct.py', base=base)],
      )
