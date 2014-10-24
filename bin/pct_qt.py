from multiprocessing import freeze_support
import sys
from exnetexplorer.main import QApplication, MainWindow


if __name__ == '__main__':
    freeze_support()
    app = QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())

