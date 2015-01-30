from multiprocessing import freeze_support
import sys
import os
from corpustools.gui.qt.main import MainWindow,QApplication

if sys.platform.startswith('win'):
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
        # Implementing dummy stdout and stderr for frozen Windows release
        class FakeSTD(object):
            def write(self, string):
                pass
            def flush(self):
                pass
        sys.stdout = FakeSTD()
        sys.stderr = FakeSTD()

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
        main.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()

