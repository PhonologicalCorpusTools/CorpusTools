
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()
        
setup(name='corpustools',
      version='0.1',
      description='',
      long_description='',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.X',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='phonology corpus phonetics',
      url='https://github.com/kchall/CorpusTools',
      author='Kathleen Currie Hall, Scott Mackie, Blake Allen, Michael Fry, Michael McAuliffe, Kevin McMullin',
      author_email='kathleen.hall@ubc.ca, mackie@email.com, b.allen@alumni.ubc.ca, mdfry20@gmail.com, michael.mcauliffe@alumni.ubc.ca, kevinmcm@alumni.ubc.ca',
      packages=['corpustools'],
      install_requires=[
          'markdown',
      ],
      include_package_data=True,
      zip_safe=False)
