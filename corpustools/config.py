
import os
import sys
import configparser

def dependencies_for_corpustools():
    from scipy.sparse.csgraph import _validation
    from scipy.special import _ufuncs_cxx

config = configparser.ConfigParser()
appname = 'CorpusTools'
appauthor = 'PCT'
if sys.platform == 'win32':
    local_data = os.path.expanduser('~\\Documents')
elif sys.platform == 'darwin':
    local_data = os.path.expanduser('~/Documents')
else:
    local_data = os.path.expanduser("~/.pct")

DEFAULT_DATA_DIR = os.path.join(local_data, appauthor, appname)
if not os.path.exists(DEFAULT_DATA_DIR):
    os.makedirs(DEFAULT_DATA_DIR)
CONFIG_PATH = os.path.join(DEFAULT_DATA_DIR,'config.ini')
LOG_DIR = os.path.join(local_data, appauthor, appname,'log')
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
ERROR_DIR = os.path.join(LOG_DIR,'ERRORS')
if not os.path.exists(ERROR_DIR):
    os.mkdir(ERROR_DIR)

if os.path.exists(CONFIG_PATH):
    config.read(CONFIG_PATH)
else:
    config['storage'] = {'directory' : DEFAULT_DATA_DIR}
    with open(CONFIG_PATH,'w') as configfile:
        config.write(configfile)
