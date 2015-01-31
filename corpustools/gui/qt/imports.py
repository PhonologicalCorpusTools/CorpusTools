

AUDIO_ENABLED = True
try:
    raise(ImportError)
    from PySide.QtCore import (QRectF, Qt, QSettings,QAbstractTableModel,
                QSize,QPoint, Signal, QThread,QModelIndex, QAbstractItemModel,
                QSharedMemory, QEvent, QIODevice, QProcess)
    from PySide.QtGui import (QFont, QLayout, QKeySequence, QPainter, QFontMetrics, QPen,
                            QRegion,QStandardItemModel,QStandardItem,
                            QMainWindow, QHBoxLayout, QLabel, QAction,
                                QApplication, QWidget, QMessageBox,QSplitter,
                                QDialog, QListWidget, QGroupBox,QVBoxLayout,
                                QPushButton, QFrame, QGridLayout,QRadioButton,
                                QFormLayout, QLineEdit, QFileDialog, QComboBox,
                                QProgressDialog, QCheckBox, QMessageBox,QTableView,
                                QAbstractItemView, QHeaderView, QDockWidget, QTreeView,
                                QStyle, QMenu, QSizePolicy, QButtonGroup,
                                QTableWidget,QSound,QItemSelection, QItemSelectionModel,
                                QToolBar, QStyledItemDelegate, QDataWidgetMapper,
                                QTabWidget)
    from PySide.QtNetwork import QLocalSocket, QLocalServer
    print('PySide version')
except ImportError:

    from PyQt5.QtCore import (QRectF, Qt, QModelIndex, QItemSelection,
                                pyqtSignal as Signal,QThread,QAbstractTableModel,
                                QSize, QSettings,QPoint, QItemSelectionModel,
                                QSortFilterProxyModel, QAbstractItemModel,
                            QSharedMemory, QEvent, QIODevice, QProcess)
    from PyQt5.QtGui import (QFont, QKeySequence, QPainter, QFontMetrics, QPen,
                            QRegion,QStandardItemModel,QStandardItem)
    from PyQt5.QtWidgets import (QMainWindow, QLayout, QHBoxLayout, QLabel, QAction,
                                QApplication, QWidget, QMessageBox,QSplitter,
                                QDialog, QListWidget, QGroupBox,QVBoxLayout,
                                QPushButton, QFrame, QGridLayout,QRadioButton,
                                QFormLayout, QLineEdit, QFileDialog, QComboBox,
                                QProgressDialog, QCheckBox, QMessageBox,QTableView,
                                QAbstractItemView, QHeaderView, QDockWidget, QTreeView,
                                QStyle, QMenu, QSizePolicy, QButtonGroup,QTabWidget,
                                QTableWidget, QToolBar, QStyledItemDelegate, QDataWidgetMapper)
    from PyQt5.QtNetwork import QLocalSocket, QLocalServer
    try:
        from PyQt5.QtMultimedia import QSound
    except MultimediaError:
        AUDIO_ENABLED = False
    print('PyQt5 version')
