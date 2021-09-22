AUDIO_ENABLED = True
HELP_ENABLED = True
try:
    from PyQt5.QtCore import (QRectF, Qt, QModelIndex, QItemSelection,
                                pyqtSignal as Signal, pyqtSlot as Slot,
                                QThread,QAbstractTableModel,QAbstractListModel,
                                QSize, QSettings,QPoint, QItemSelectionModel,
                                QSortFilterProxyModel, QAbstractProxyModel, QAbstractItemModel,
                                QSharedMemory, QEvent, QIODevice, QProcess, QUrl, QTime,
                                QStringListModel)
    from PyQt5.QtGui import (QFont, QKeySequence, QPainter, QFontMetrics, QPen,
                            QRegion,QStandardItemModel,QStandardItem, QIcon, QPixmap,
                            QDesktopServices, QCursor, QDoubleValidator)
    from PyQt5.QtWidgets import (QMainWindow, QLayout, QHBoxLayout, QLabel, QAction,
                                QApplication, QWidget, QMessageBox,QSplitter,
                                QDialog, QListWidget, QGroupBox,QVBoxLayout,
                                QPushButton, QFrame, QGridLayout,QRadioButton,
                                QFormLayout, QLineEdit, QFileDialog, QComboBox,
                                QProgressDialog, QCheckBox, QMessageBox,QTableView,
                                QAbstractItemView, QHeaderView, QDockWidget, QTreeView,
                                QStyle, QMenu, QSizePolicy, QButtonGroup,QTabWidget,
                                QTableWidget, QToolBar, QStyledItemDelegate, QDataWidgetMapper,
                                QSlider, QItemDelegate, QScrollArea, QBoxLayout, QStackedWidget,
                                QCompleter, QTableWidgetItem)
    from PyQt5.QtNetwork import QLocalSocket, QLocalServer

    # The following chunk for importing QWebView can be removed. We are not using it anymore.
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView #This is required for PyQt5.9
    except ImportError:
        try:
            from PyQt5.QtWebKitWidgets import QWebView
        except ImportError:
            HELP_ENABLED = False

    try:
        from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent, QAudioOutput
    except ImportError:
        AUDIO_ENABLED = False

    class QHLine(QFrame):
        def __init__(self):
            super(QHLine, self).__init__()
            self.setFrameShape(QFrame.HLine)
            self.setFrameShadow(QFrame.Sunken)


    class QVLine(QFrame):
        def __init__(self):
            super(QVLine, self).__init__()
            self.setFrameShape(QFrame.VLine)
            self.setFrameShadow(QFrame.Sunken)

except ImportError:
    raise(Exception("We could not find an installation of PyQt5.  Please double check that it is installed."))

import locale
import sys
if sys.platform.startswith('win'):
    locale_string = 'English_US'
else:
    locale_string = 'en_US.UTF-8'
locale.setlocale(locale.LC_ALL, locale_string)

import time
