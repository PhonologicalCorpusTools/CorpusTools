from .imports import *


class SwitchDelegate(QItemDelegate):
    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        switch = QPushButton(parent)
        switch.setCheckable(False)
        switch.setAutoExclusive(False)
        if sys.platform == 'darwin' or sys.platform.startswith('win'):
            icon = QIcon()
            icon.addPixmap(QPixmap(":/Icon/resources/object-flip-horizontal.png"),
                        QIcon.Normal, QIcon.Off)
        else:
            icon = QIcon.fromTheme('object-flip-horizontal')
        switch.setIcon(icon)
        switch.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        switch.setMaximumSize(switch.iconSize().width()+14,switch.iconSize().height()+14)
        switch.clicked.connect(lambda : self.click(index=index))
        switch.setFocusPolicy(Qt.NoFocus)
        return switch

    def click(self, index):
        index.model().switchRow(index.row())
