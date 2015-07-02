

import functools

from corpustools.exceptions import PCTError, PCTPythonError

def check_for_errors(function):
    @functools.wraps(function)
    def do_check(*args,**kwargs):
        self = args[0]
        try:
            function(*args,**kwargs)
        except PCTError as e:
            if not hasattr(self, 'handleError'):
                raise
            self.handleError(e)
        except Exception as e:
            if not hasattr(self, 'handleError'):
                raise
            e = PCTPythonError(e)
            self.handleError(e)
    return do_check
