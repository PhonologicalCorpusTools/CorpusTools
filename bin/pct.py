from multiprocessing import freeze_support
import sys
from corpustools.gui.qt.main import MainWindow,QApplication

def main():
    freeze_support()
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

