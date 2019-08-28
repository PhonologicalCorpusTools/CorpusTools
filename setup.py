import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

import corpustools

def readme():
    with open('README.md') as f:
        return f.read()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(name='corpustools',
      version=corpustools.__version__,
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
                'corpustools.command_line'],
      dependency_links = ['https://github.com/kylebgorman/textgrid/tarball/master#egg=textgrid-1.0'],
      install_requires=[
          'numpy',
          'scipy',
          'textgrid',
          'pyqt'
          #'python-acoustic-similarity'
      ],
      entry_points = {
        'console_scripts': ['pct=corpustools.command_line.pct:main',
                            'pct_corpus=corpustools.command_line.pct_corpus:main',
                            'pct_funcload=corpustools.command_line.pct_funcload:main',
                            'pct_neighdens=corpustools.command_line.pct_neighdens:main',
                            'pct_mutualinfo=corpustools.command_line.pct_mutualinfo:main',
                            'pct_kl=corpustools.command_line.pct_kl:main',
                            'pct_search=corpustools.command_line.pct_search:main',
                            'pct_visualize=corpustools.command_line.pct_visualize:main'],
    },
    cmdclass={'test': PyTest},
    extras_require={
        'testing': ['pytest'],
    }
      )
