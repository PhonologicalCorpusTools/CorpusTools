try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='corpustools',
      version='1.0.0',
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
                'corpustools.gui',
                'corpustools.symbolsim',
                'corpustools.neighdens',
                'corpustools.mutualinfo',
                'corpustools.phonoprob',
                'corpustools.command_line'],
      install_requires=[
          'numpy',
          'scipy'
      ],
      entry_points = {
        'console_scripts': ['pct=corpustools.command_line.pct:main',
                            'pct_corpus=corpustools.command_line.pct_corpus:main',
                            'pct_funcload=corpustools.command_line.pct_funcload:main',
                            'pct_neighdens=corpustools.command_line.pct_neighdens:main',
                            'pct_mutualinfo=corpustools.command_line.pct_mutualinfo:main',
                            'pct_search=corpustools.command_line.pct_search:main'],
    },
      )
