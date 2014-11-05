
from urllib.request import urlretrieve

import pickle

def download_binary(name,path, queue = None):
    """
    Download a binary file

    Attributes
    ----------
    name : str
        Identifier of file to download

    path : str
        Full path for where to save downloaded file

    """
    def report(blocknum, bs, size):
        if queue is not None:
            queue.put((blocknum * bs * 100) / size)
    if name == 'example':
        download_link = 'https://www.dropbox.com/s/a0uar9h8wtem8cf/example.corpus?dl=1'
    elif name == 'iphod':
        download_link = 'https://www.dropbox.com/s/xb16h5ppwmo579s/iphod.corpus?dl=1'
    elif name == 'spe':
        download_link = 'https://www.dropbox.com/s/k73je4tbk6i4u4e/spe.feature?dl=1'
    elif name == 'hayes':
        download_link = 'https://www.dropbox.com/s/qe9xiq4k68cp2qx/hayes.feature?dl=1'
    filename,headers = urlretrieve(download_link,path, reporthook=report)
    if queue is not None:
        queue.put(-99)

def load_binary(path):
    """
    Unpickle a binary file

    Attributes
    ----------
    path : str
        Full path of binary file to load

    Returns
    -------
    Object
        Object generated from the text file
    """
    #begin = time.time()
    with open(path,'rb') as f:
        obj = pickle.load(f)
    #print("Load binary time: ",time.time()-begin)
    return obj

def save_binary(obj,path):
    """
    Pickle a Corpus or FeatureMatrix object for later loading

    Attributes
    ----------
    obj : Corpus or FeatureMatrix
        Object to save

    path : str
        Full path for where to save object

    """
    with open(path,'wb') as f:
        pickle.dump(obj,f)
