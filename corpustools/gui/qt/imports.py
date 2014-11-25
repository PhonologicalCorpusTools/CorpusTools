
try:
    raise(ImportError)
    from PySide.QtCore import (QRectF, Qt, QSettings,QAbstractTableModel,
                QSize,QPoint, Signal, QThread,QModelIndex)
    from PySide.QtGui import (QFont, QKeySequence, QPainter, QFontMetrics, QPen,
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
                                QToolBar, QStyledItemDelegate)

    print('PySide version')
except ImportError:

    from PyQt5.QtCore import (QRectF, Qt, QModelIndex, QItemSelection,
                                pyqtSignal as Signal,QThread,QAbstractTableModel,
                                QSize, QSettings,QPoint)
    from PyQt5.QtGui import (QFont, QKeySequence, QPainter, QFontMetrics, QPen,
                            QRegion,QStandardItemModel,QStandardItem)
    from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QLabel, QAction,
                                QApplication, QWidget, QMessageBox,QSplitter,
                                QDialog, QListWidget, QGroupBox,QVBoxLayout,
                                QPushButton, QFrame, QGridLayout,QRadioButton,
                                QFormLayout, QLineEdit, QFileDialog, QComboBox,
                                QProgressDialog, QCheckBox, QMessageBox,QTableView,
                                QAbstractItemView, QHeaderView, QDockWidget, QTreeView,
                                QStyle, QMenu, QSizePolicy, QButtonGroup,
                                QTableWidget, QToolBar, QStyledItemDelegate)
    from PyQt5.QtMultimedia import QSound
    print('PyQt5 version')
