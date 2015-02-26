

AUDIO_ENABLED = True
HELP_ENABLED = True
try:
    from PyQt5.QtCore import (QRectF, Qt, QModelIndex, QItemSelection,
                                pyqtSignal as Signal,QThread,QAbstractTableModel,
                                QSize, QSettings,QPoint, QItemSelectionModel,
                                QSortFilterProxyModel, QAbstractItemModel,
                            QSharedMemory, QEvent, QIODevice, QProcess, QUrl, QTime)
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
                                QTableWidget, QToolBar, QStyledItemDelegate, QDataWidgetMapper,
                                QSlider)
    from PyQt5.QtNetwork import QLocalSocket, QLocalServer
    try:
        from PyQt5.QtWebKitWidgets import QWebView
    except ImportError:
        HELP_ENABLED = False
    try:
        from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent, QAudioOutput
    except ImportError:
        AUDIO_ENABLED = False
    #print('PyQt5 version')
except ImportError:
    raise(Exception("We could not find an installation of PyQt5.  Please double check that it is installed."))
