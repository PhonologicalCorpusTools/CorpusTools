
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
        download_link = 'https://www.dropbox.com/s/fb7txi4c1rf8lbx/example.corpus?dl=1'
    elif name == 'lemurian':
        download_link = 'https://www.dropbox.com/s/o98q83bq5derf3u/lemurian.corpus?dl=1'
    elif name == 'iphod_with_homographs':
        download_link = 'https://www.dropbox.com/s/qgu6mu38arubu6s/iphod_with_homographs.corpus?dl=1'
    elif name == 'iphod_without_homographs':
        download_link = 'https://www.dropbox.com/s/snlpehx157kfgbu/iphod_without_homographs.corpus?dl=1'
    elif name == 'ipa2spe':
        download_link = 'https://www.dropbox.com/s/5jy86fpuhrmrq6c/ipa2spe.feature?dl=1'
    elif name == 'ipa2hayes':
        download_link = 'https://www.dropbox.com/s/cmg7om0vy84jav2/ipa2hayes.feature?dl=1'
    elif name == 'celex2spe':
        download_link = 'https://www.dropbox.com/s/8rp0abitda0euan/celex2spe.feature?dl=1'
    elif name == 'celex2hayes':
        download_link = 'https://www.dropbox.com/s/fife4ajchf2smc4/celex2hayes.feature?dl=1'
    elif name == 'arpabet2spe':
        download_link = 'https://www.dropbox.com/s/v768usixjurotzj/arpabet2spe.feature?dl=1'
    elif name == 'arpabet2hayes':
        download_link = 'https://www.dropbox.com/s/hrkouyzx6bvb274/arpabet2hayes.feature?dl=1'
    elif name == 'cpa2spe':
        download_link = 'https://www.dropbox.com/s/d1zs9w4p1yo1971/cpa2spe.feature?dl=1'
    elif name == 'cpa2hayes':
        download_link = 'https://www.dropbox.com/s/wglm3fuhxivnc8g/cpa2hayes.feature?dl=1'
    elif name == 'disc2spe':
        download_link = 'https://www.dropbox.com/s/3136ajvpla8wvi5/disc2spe.feature?dl=1'
    elif name == 'disc2hayes':
        download_link = 'https://www.dropbox.com/s/9dxns42axzsbhht/disc2hayes.feature?dl=1'
    elif name == 'klatt2spe':
        download_link = 'https://www.dropbox.com/s/vzh0h3s9m28m5hj/klatt2spe.feature?dl=1'
    elif name == 'klatt2hayes':
        download_link = 'https://www.dropbox.com/s/hwfewt2ti4kh5e1/klatt2hayes.feature?dl=1'
    elif name == 'sampa2spe':
        download_link = 'https://www.dropbox.com/s/5w64o9lavz9eyum/sampa2spe.feature?dl=1'
    elif name == 'sampa2hayes':
        download_link = 'https://www.dropbox.com/s/4dq063yvi4ak5n1/sampa2hayes.feature?dl=1'
    elif name == 'buckeye2spe':
        download_link = 'https://www.dropbox.com/s/nkfizg3a0x4497m/buckeye2spe.feature?dl=1'
    elif name == 'buckeye2hayes':
        download_link = 'https://www.dropbox.com/s/37rv5j4lm9hcyxn/buckeye2hayes.feature?dl=1'
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
        self.metastack = [] # for compatability with Python 3.6
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