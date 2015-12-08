#!/bin/sh
set -e
#check to see if miniconda folder is empty
if [ ! -d "$HOME/cachedir/miniconda/envs/test-environment" ]; then
  wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
  chmod +x miniconda.sh
  ./miniconda.sh -b -p $HOME/cachedir/miniconda
  export PATH="$HOME/cachedir/miniconda/bin:$PATH"
  conda config --set always_yes yes --set changeps1 no
  conda config --add channels dsdale24
  conda update -q conda
  conda info -a
  conda create -q -n test-environment python=$TRAVIS_PYTHON_VERSION atlas numpy scipy pytest
else
  echo "Miniconda already installed."
fi

source activate test-environment
which python

# check to see if sip folder is empty
if [ ! -d "$HOME/cachedir/sip/bin" ]; then
  wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.6/sip-4.16.6.tar.gz
  tar -xzf sip-4.16.6.tar.gz
  cd sip-4.16.6 && python configure.py -b $HOME/cachedir/sip/bin -e $HOME/cachedir/sip/include -v $HOME/cachedir/sip && make && make install
else
  echo "Using cached sip directory."
fi

# check to see if pyqt5 folder is empty
if [ ! -d "$HOME/cachedir/pyqt5/bin" ]; then
  wget http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.4.1/PyQt-gpl-5.4.1.tar.gz
  tar -xzf PyQt-gpl-5.4.1.tar.gz
  cd PyQt-gpl-5.4.1 && python configure.py  -c --confirm-license --no-designer-plugin --no-qml-plugin -b $HOME/cachedir/pyqt5/bin -v $HOME/cachedir/sip/PyQt5 --sip=$HOME/cachedir/sip/bin/sip --sip-incdir=$HOME/cachedir/sip/include && make && make install
  git clone https://github.com/mmcauliffe/pytest-qt.git
  cd pytest-qt && python setup.py install
  pip install coveralls pytest-cov
else
  echo "Using cached pyqt5 directory."
fi


