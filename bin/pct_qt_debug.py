import os
import sys
base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0,base)
import corpustools.gui.main as Main #import MainWindow,QApplicationMessaging

if __name__ == '__main__':

    app = Main.QApplicationMessaging(sys.argv)
    if app.isRunning():
        if len(sys.argv) > 1:
            app.sendMessage(sys.argv[1])
        else:
            app.sendMessage('ARISE')
    else:
        main = Main.MainWindow(app)

        app.aboutToQuit.connect(main.cleanUp)
        app.setActiveWindow(main)
        main.show()
        sys.exit(app.exec_())
