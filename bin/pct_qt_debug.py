
import os
import sys
base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(base)
from corpustools.gui.qt.main import MainWindow,QApplication

if __name__ == '__main__':

    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
