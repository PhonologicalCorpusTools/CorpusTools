#!/usr/bin/env python
import sys
import os

if sys.platform.startswith('win'):
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.expanduser('~/Documents'))
        # Implementing dummy stdout and stderr for frozen Windows release
        class FakeSTD(object):
            def write(self, string):
                pass
            def flush(self):
                pass
        #This should fix stdout flush errors, but doesn't always
        #Also needs a small tweak to multiprocessing.process._bootstrap
        sys.stdout = FakeSTD()
        sys.stderr = FakeSTD()

from multiprocessing import freeze_support
from corpustools.gui.main import MainWindow,QApplicationMessaging

def main():
    freeze_support()

    app = QApplicationMessaging(sys.argv)
    if app.isRunning():
        if len(sys.argv) > 1:
            app.sendMessage(sys.argv[1])
        else:
            app.sendMessage('ARISE')
    else:
        main = MainWindow(app)
        app.aboutToQuit.connect(main.cleanUp)

        app.setActiveWindow(main)
        main.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()

