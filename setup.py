try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='corpustools',
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
      author='Phonological Corpus Tools',
      author_email='kathleen.hall@ubc.ca',
      packages=['corpustools',
                'bin',
                'corpustools.acousticsim',
                'corpustools.corpus',
                'corpustools.corpus.classes',
                'corpustools.corpus.io',
                'corpustools.freqalt',
                'corpustools.funcload',
                'corpustools.prod',
                'corpustools.gui',
                'corpustools.gui.qt',
                'corpustools.symbolsim',
                'corpustools.neighdens',
                'corpustools.mutualinfo',
                'corpustools.phonoprob',
                'command_line'],
      #install_requires=[
      #    'pillow'
      #],
      entry_points = {
        'console_scripts': ['pct=bin.pct:main',
                            'pct_corpus=command_line.pct_corpus:main',
                            'pct_funcload=command_line.pct_funcload:main',
                            'pct_neighdens=command_line.pct_neighdens:main',
                            'pct_mutualinfo=command_line.pct_mutualinfo:main'],
    },
    scripts=['bin/pct.py']
      )
