
from urllib.request import urlretrieve
import pickle
import os

def download_binary(name, path, call_back = None):
    """
    Download a binary file of example corpora and feature matrices.

    Names of available corpora: 'example', 'iphod', 'lemurian'

    Names of available feature matrices: 'ipa2spe', 'ipa2hayes',
    'celex2spe', 'celex2hayes', 'arpabet2spe', 'arpabet2hayes',
    'cpa2spe', 'cpa2hayes', 'disc2spe', 'disc2hayes', 'klatt2spe',
    'klatt2hayes', 'sampa2spe', and 'sampa2hayes'

    Parameters
    ----------
    name : str
        Identifier of file to download

    path : str
        Full path for where to save downloaded file

    call_back : callable
        Function that can handle strings (text updates of progress),
        tuples of two integers (0, total number of steps) and an integer
        for updating progress out of the total set by a tuple

    Returns
    -------
    bool
        True if file was successfully saved to the path specified, False
        otherwise

    """
    reported_size = False
    if call_back is not None:
        call_back('Downloading file...')
    def report(blocknum, bs, size):
        if call_back is not None:
            nonlocal reported_size
            if not reported_size:
                reported_size = True
                call_back(0,size)
            call_back(blocknum * bs)
    if name == 'example':
        download_link = 'https://www.dropbox.com/s/6ppb7d9l1kh6gkm/example.corpus?dl=1'
    elif name == 'lemurian':
        download_link = 'https://www.dropbox.com/s/76aiyi2c5qa6mlz/lemurian.corpus?dl=1'
    elif name == 'iphod':
        download_link = 'https://www.dropbox.com/s/8s7o8trddk0c5tw/iphod.corpus?dl=1'
    elif name == 'ipa2spe':
        download_link = 'https://www.dropbox.com/s/g6lsnxacc81ot26/ipa2spe.feature?dl=1'
    elif name == 'ipa2hayes':
        download_link = 'https://www.dropbox.com/s/lqhyux5mzx46x15/ipa2hayes.feature?dl=1'
    elif name == 'celex2spe':
        download_link = 'https://www.dropbox.com/s/mzpn1w27gtqo965/celex2spe.feature?dl=1'
    elif name == 'celex2hayes':
        download_link = 'https://www.dropbox.com/s/gtn4cn849ab5rky/celex2hayes.feature?dl=1'
    elif name == 'arpabet2spe':
        download_link = 'https://www.dropbox.com/s/g1yhfc1951ztzdt/arpabet2spe.feature?dl=1'
    elif name == 'arpabet2hayes':
        download_link = 'https://www.dropbox.com/s/gt6ow1duk97mpyk/arpabet2hayes.feature?dl=1'
    elif name == 'cpa2spe':
        download_link = 'https://www.dropbox.com/s/mekaqc4kkbz7d1l/cpa2spe.feature?dl=1'
    elif name == 'cpa2hayes':
        download_link = 'https://www.dropbox.com/s/4e057221f6ciwix/cpa2hayes.feature?dl=1'
    elif name == 'disc2spe':
        download_link = 'https://www.dropbox.com/s/jpfrpnq7b2myfd6/disc2spe.feature?dl=1'
    elif name == 'disc2hayes':
        download_link = 'https://www.dropbox.com/s/v1t99ys3t8w0guf/disc2hayes.feature?dl=1'
    elif name == 'klatt2spe':
        download_link = 'https://www.dropbox.com/s/7yqm7xark4l3p0h/klatt2spe.feature?dl=1'
    elif name == 'klatt2hayes':
        download_link = 'https://www.dropbox.com/s/9e8mtf45rwme9jo/klatt2hayes.feature?dl=1'
    elif name == 'sampa2spe':
        download_link = 'https://www.dropbox.com/s/4ymm9789xhrvxid/sampa2spe.feature?dl=1'
    elif name == 'sampa2hayes':
        download_link = 'https://www.dropbox.com/s/ch5yzlisoeaz58e/sampa2hayes.feature?dl=1'
    elif name == 'buckeye2spe':
        download_link = 'https://www.dropbox.com/s/p8cazx943ky8i3z/buckeye2spe.feature?dl=1'
    elif name == 'buckeye2hayes':
        download_link = 'https://www.dropbox.com/s/oi58pqd8dzl7puu/Buckeye2hayes.feature?dl=1'
    else:
        return False
    filename, headers = urlretrieve(download_link, path, reporthook=report)
    return True

def load_binary(path):
    """
    Unpickle a binary file

    Parameters
    ----------
    path : str
        Full path of binary file to load

    Returns
    -------
    Object
        Object generated from the text file
    """
    with open(path,'rb') as f:
        obj = pickle.load(f)
    return obj

def save_binary(obj, path):
    """
    Pickle a Corpus or FeatureMatrix object for later loading

    Parameters
    ----------
    obj : Corpus or FeatureMatrix
        Object to save

    path : str
        Full path for where to save object

    """
    with open(path,'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


class PCTUnpickler(pickle._Unpickler):

    def __init__(self, path, call_back = None, stop_check = None):
        self.path = path
        self.file = open(path, mode='rb')
        self.call_back = call_back
        self.stop_check = stop_check
        super().__init__(self.file)

    def __del__(self):
        self.file.close()

    def load(self):
        """Read a pickled object representation from the open file.

        Return the reconstituted object hierarchy specified in the file.
        """
        # Check whether Unpickler was initialized correctly. This is
        # only needed to mimic the behavior of _pickle.Unpickler.dump().
        if not hasattr(self, "_file_read"):
            raise pickle.UnpicklingError("Unpickler.__init__() was not called by "
                                  "%s.__init__()" % (self.__class__.__name__,))
        self._unframer = pickle._Unframer(self._file_read, self._file_readline)
        self.read = self._unframer.read
        self.readline = self._unframer.readline
        self.mark = object()  # any new unique object
        self.stack = []
        self.append = self.stack.append
        self.proto = 0
        read = self.read
        dispatch = self.dispatch
        if self.call_back is not None:
            self.call_back('Loading...')
            self.call_back(0, os.path.getsize(self.path))
            cur = 0
        n = 0
        try:
            while True:
                n+=1
                if n == 1024:
                    n = 0
                    if self.stop_check is not None and self.stop_check():
                        self.file.close()
                        raise pickle._Stop(None)
                    if self.call_back is not None:
                        cur += 1
                        self.call_back(cur)
                key = read(1)
                if not key:
                    raise EOFError
                assert isinstance(key, (bytes, bytearray))
                dispatch[key[0]](self)
        except pickle._Stop as stopinst:
            return stopinst.value