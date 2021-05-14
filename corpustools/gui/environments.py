from .imports import *
from .widgets import SegmentSelectionWidget, SegmentSelectDialog
from corpustools.corpus.classes.lexicon import EnvironmentFilter, SyllableEnvironmentFilter
import sip
from pprint import pprint
import regex as re

SPECIAL_SYMBOL_RE = ['.', '^', '$', '*', '+', '?', '|', '{', '}', '[', ']', '#', '(', ')', '\'', '\"']


class EnvironmentDialog(QDialog):
    rowToAdd = Signal(str)
    def __init__(self, inventory,parent=None):
        QDialog.__init__(self,parent)

        self.inventory = inventory

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.lhsEnvFrame = QGroupBox('Left hand side')

        self.rhsEnvFrame = QGroupBox('Right hand side')

        lhsEnvLayout = QVBoxLayout()

        lhsEnvLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        rhsEnvLayout = QVBoxLayout()

        rhsEnvLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.lhs = SegmentSelectionWidget(self.inventory, exclusive = True)

        self.rhs = SegmentSelectionWidget(self.inventory, exclusive = True)

        lhsEnvLayout.addWidget(self.lhs)
        rhsEnvLayout.addWidget(self.rhs)

        self.lhsEnvFrame.setLayout(lhsEnvLayout)

        self.rhsEnvFrame.setLayout(rhsEnvLayout)
        envFrame = QFrame()

        envLayout = QHBoxLayout()

        envLayout.addWidget(self.lhsEnvFrame)
        envLayout.addWidget(self.rhsEnvFrame)

        envFrame.setLayout(envLayout)

        layout.addWidget(envFrame)

        self.oneButton = QPushButton('Add')
        self.anotherButton = QPushButton('Add and create another')
        self.cancelButton = QPushButton('Cancel')
        self.acLayout = QHBoxLayout()
        self.acLayout.addWidget(self.oneButton, alignment = Qt.AlignLeft)
        self.acLayout.addWidget(self.anotherButton, alignment = Qt.AlignLeft)
        self.acLayout.addWidget(self.cancelButton, alignment = Qt.AlignLeft)
        self.oneButton.clicked.connect(self.one)
        self.anotherButton.clicked.connect(self.another)
        self.cancelButton.clicked.connect(self.reject)

        acFrame = QFrame()
        acFrame.setLayout(self.acLayout)

        layout.addWidget(acFrame, alignment = Qt.AlignLeft)
        self.addOneMore = False
        self.setLayout(layout)
        #self.setFixedSize(self.sizeHint())
        self.setWindowTitle('Create bigram')

    def one(self):
        self.addOneMore = False
        self.accept()

    def another(self):
        self.addOneMore = True
        self.accept()

    def reset(self):
        self.lhs.clearAll()
        self.rhs.clearAll()

    def accept(self):
        lhs = self.lhs.value()
        rhs = self.rhs.value()

        if lhs == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a left hand of the bigram.")
            return
        if rhs == '':
            reply = QMessageBox.critical(self,
                    "Missing information", "Please specify a right hand of the bigram.")
            return

        env = lhs, rhs
        self.rowToAdd.emit([env])
        if not self.addOneMore:
            QDialog.accept(self)
        else:
            self.reset()


class EnvironmentSegmentWidget(QWidget):
    segDeleted = Signal(list)

    def __init__(self, inventory, parent=None, middle=False, enabled=True, preset_label=False,
                 show_full_inventory=False, side=None, allow_zero_match=False):
        QWidget.__init__(self, parent)
        self.inventory = inventory
        self.segments = set()
        self.features = set()
        self.parent_ = parent
        self.enabled = enabled
        self.show_full_inventory = show_full_inventory
        self.side = side
        self.allowZeroMatch = allow_zero_match
        self.middle = middle

        layout = QVBoxLayout()
        if self.middle:
            lab = '_\n\n{}'
        else:
            lab = '{}'

        self.mainLabel = QPushButton(lab)
        self.mainLabel.setStyleSheet("padding: 4px")

        layout.addWidget(self.mainLabel)

        self.setLayout(layout)

        if self.enabled:
            self.menu = QMenu(self)
            segmentAct = QAction("Add segments", self, triggered=self.selectSegments)
            featureAct = QAction("Add features", self, triggered=self.selectFeatures)
            clearAct = QAction("Clear selection", self, triggered=self.clearSelection)
            matchAnythingAct = QAction("Match single wildcard", self, triggered=self.addArbitrary)
            self.menu.addAction(segmentAct)
            self.menu.addAction(featureAct)

            if not self.middle:
                nonSegSelectMenu = self.menu.addMenu('Add non-segment symbol')
                for symbol in self.inventory.non_segment_symbols:
                    nonSegSelectMenu.addAction(QAction(symbol, self, triggered=self.addNonSegSymbol))
            self.menu.addAction(matchAnythingAct)
            self.menu.addAction(clearAct)
            if not self.middle:
                deleteAct = QAction("Delete", self, triggered=self.deleteSelection)
                self.menu.addAction(deleteAct)
            self.mainLabel.setMenu(self.menu)
            addNewPosMenu = self.menu.addMenu("Add new environment position")
            addToLeftAct = QAction("To the left", self, triggered=self.addToLeft)
            addToRightAct = QAction("To the right", self, triggered=self.addToRight)
            addNewPosMenu.addAction(addToLeftAct)
            addNewPosMenu.addAction(addToRightAct)
            if not self.middle:
                self.allowZeroAct = QAction("Make this position optional", self, checkable=True, triggered=self.setZeroMatching)
                self.menu.addAction(self.allowZeroAct)
        else:
            self.mainLabel.setEnabled(False)

        if preset_label:
            self.segments = preset_label.segments
            self.features = preset_label.features
            self.updateLabel()

    def setZeroMatching(self, b):
        self.allowZeroMatch = self.allowZeroAct.isChecked()

    def addToLeft(self):
        self.parent_.insertSegWidget(self, 'l')

    def addToRight(self):
        self.parent_.insertSegWidget(self, 'r')

    def addNonSegSymbol(self):
        self.segments.add(self.sender().text())
        self.updateLabel()

    def addArbitrary(self):
        self.segments = set(self.inventory.segs)
        self.updateLabel()

    def clearSelection(self):
        self.segments = set()
        self.features = set()
        self.updateLabel()

    def deleteSelection(self):
        self.segDeleted.emit([self]) #connected to EnvironmentSegmentWidget.deleteSeg()

    def updateLabel(self):
        labelText = self.generateDisplayText()
        if not labelText:
             labelText = '{}'
        if self.middle:
            labelText = '_\n\n{}'.format(labelText)
        self.mainLabel.setText(labelText)

    def generateDisplayText(self):
        displayList = list()
        if len(self.segments) == len(self.inventory.segs):
            if self.show_full_inventory:
                displayList = ','.join(self.segments)
            else:
                displayList = '{*}'
        else:
            displayList.extend(self.segments)
            displayList.extend(self.features)
            displayList = ','.join(displayList)
            displayList = '{{{}}}'.format(displayList)

        return displayList

    def selectSegments(self):
        dialog = SegmentSelectDialog(self.inventory, self.segments, self, start_pressed=self.segments)
        if dialog.exec_():
            self.segments = set(dialog.value())
            self.updateLabel()

    def selectFeatures(self):
        dialog = SegmentSelectDialog(self.inventory, self.segments, self, use_features=True)
        if dialog.exec_():
            self.features = set(dialog.value())
            self.updateLabel()

    def value(self):
        segs = [s for s in self.segments]
        if self.features:
            more_segs = self.inventory.features_to_segments(self.features)
            segs.extend(more_segs)
            segs = list(set(segs))
        return segs

    def displayValue(self):
        return self.generateDisplayText()

    def getData(self):
        attrs = ['inventory', 'segments', 'features', 'inventory', 'middle', 'enabled',
                 'show_full_inventory', 'side', 'allowZeroMatch']
        return {attr: getattr(self, attr) for attr in attrs}

    def loadData(self, data):
        for k, v in data.items(): #see the getData() function above for details
            setattr(self, k, v)


class EnvironmentSelectWidget(QGroupBox):
    def __init__(self, inventory, parent=None, middle=True, show_full_inventory=False, single_env=False, mode='segMode'):
        QGroupBox.__init__(self, 'Environments', parent)
        self.parent = parent
        self.middle = middle
        self.inventory = inventory
        self.show_full_inventory = show_full_inventory
        self.single_env = single_env
        self.mode = mode

        layout = QVBoxLayout()

        scroll = QScrollArea()

        self.environmentFrame = QWidget()

        lay = QBoxLayout(QBoxLayout.TopToBottom)
        self.addButton = QPushButton('New environment')
        self.addButton.clicked.connect(self.addNewEnvironment)
        lay.addWidget(self.addButton)
        lay.addStretch()
        self.environmentFrame.setLayout(lay)

        scroll.setWidgetResizable(True)
        scroll.setWidget(self.environmentFrame)
        scroll.setMinimumWidth(140)
        scroll.setMinimumHeight(200)

        policy = scroll.sizePolicy()
        policy.setVerticalStretch(1)
        scroll.setSizePolicy(policy)
        layout.addWidget(scroll)

        self.setLayout(layout)
        self.setMinimumWidth(500)

    def addNewEnvironment(self):
        if self.mode == 'segMode':
            envWidget = EnvironmentWidget(self.inventory, middle=self.middle, parent=self, show_full_inventory=self.show_full_inventory)
        else:
            envWidget = EnvironmentSyllableWidget(self.inventory, middle=self.middle, parent=self, show_full_inventory=self.show_full_inventory)
        pos = self.environmentFrame.layout().count() - 2
        self.environmentFrame.layout().insertWidget(pos, envWidget)
        if self.single_env:
            self.addButton.setEnabled(False)

    @Slot(list)  # connected to EnvironmentWidget.envCopied()
    def addCopiedEnvironment(self, args):
        copy_data = args[0] if args else None
        if self.mode == 'segMode':
            envWidget = EnvironmentWidget(self.inventory, middle=copy_data.middle, parent=self, copy_data=copy_data)
        else:
            envWidget = EnvironmentSyllableWidget(self.inventory, middle=copy_data.middle, parent=self,
                                                  copy_data=copy_data)
        pos = self.environmentFrame.layout().count() - 2
        self.environmentFrame.layout().insertWidget(pos, envWidget)

    def value(self):
        envs = []
        for ind in range(self.environmentFrame.layout().count() - 2):
            wid = self.environmentFrame.layout().itemAt(ind).widget()
            envs.append(wid.value())  # wid here is EnvironmentWidget, and value() returns an EnvFilter
        return envs

    def displayValue(self):
        # TODO: need to change this part to fit the new sylmode
        envs = []
        for ind in range(self.environmentFrame.layout().count() - 2):
            wid = self.environmentFrame.layout().itemAt(ind).widget()
            envs.append(wid.displayValue())
        return envs


class EnvironmentWidget(QWidget):
    envCopied = Signal(list)

    def __init__(self, inventory, parent=None, middle=True, copy_data=None, show_full_inventory=False):
        QWidget.__init__(self)
        self.inventory = inventory
        self.parent = parent
        self.middle = middle
        self.show_full_inventory = show_full_inventory
        self.envCopied.connect(self.parent.addCopiedEnvironment)
        layout = QHBoxLayout()

        self.lhsAddNew = QPushButton('+')
        self.lhsAddNew.setFixedWidth(50)
        self.lhsAddNew.clicked.connect(self.addLhs)

        self.lhsWidget = QWidget()
        self.lhsLayout = QHBoxLayout()
        self.lhsWidget.setLayout(self.lhsLayout)

        self.rhsAddNew = QPushButton('+')
        self.rhsAddNew.setFixedWidth(50)
        self.rhsAddNew.clicked.connect(self.addRhs)

        self.rhsWidget = QWidget()
        self.rhsLayout = QHBoxLayout()
        self.rhsWidget.setLayout(self.rhsLayout)

        self.middleWidget = EnvironmentSegmentWidget(self.inventory, parent=self, middle=True, enabled=middle,
                                                     show_full_inventory=show_full_inventory)

        self.removeButton = QPushButton('Remove environment')
        self.removeButton.clicked.connect(self.deleteEnvironment)
        self.copyButton = QPushButton('Copy environment')
        self.copyButton.clicked.connect(self.copyEnvironment)
        if self.parent.single_env:
            self.copyButton.setEnabled(False)

        layout.addWidget(self.lhsAddNew)
        layout.addWidget(self.lhsWidget)
        layout.addWidget(self.middleWidget)
        layout.addWidget(self.rhsWidget)
        layout.addWidget(self.rhsAddNew)

        layout.addStretch()

        optionlayout = QVBoxLayout()
        optionlayout.addWidget(self.removeButton)
        optionlayout.addWidget(self.copyButton)

        layout.addLayout(optionlayout)

        self.setLayout(layout)
        if copy_data:
            self.loadfromCopy(copy_data)

    def loadfromCopy(self, copy_data):
        self.middleWidget.segments = copy_data.middleWidget.segments
        self.middleWidget.features = copy_data.middleWidget.features
        self.middleWidget.mainLabel.setText(copy_data.middleWidget.mainLabel.text())

        for ind in range(copy_data.lhsWidget.layout().count()):
            copy_wid = copy_data.lhsWidget.layout().itemAt(ind).widget()
            wid = EnvironmentSegmentWidget(self.inventory, parent=self, preset_label=copy_wid, side='l',
                                                                allow_zero_match=copy_wid.allowZeroMatch)
            wid.allowZeroAct.setChecked(copy_wid.allowZeroMatch)
            self.lhsWidget.layout().insertWidget(ind, wid)
            wid.segDeleted.connect(self.deleteSeg)
        for ind in range(copy_data.rhsWidget.layout().count()):
            copy_wid = copy_data.rhsWidget.layout().itemAt(ind).widget()
            wid = EnvironmentSegmentWidget(self.inventory, parent=self, preset_label=copy_wid, side='r',
                                                                allow_zero_match=copy_wid.allowZeroMatch)
            wid.allowZeroAct.setChecked(copy_wid.allowZeroMatch)
            self.rhsWidget.layout().insertWidget(ind, wid)
            wid.segDeleted.connect(self.deleteSeg)

    def copyEnvironment(self):
        self.envCopied.emit([self])  # connected to EnvironmentSelectWidget.addCopiedEnvironment()

    def deleteEnvironment(self):
        self.parent.addButton.setEnabled(True)
        self.deleteLater()

    def insertSegWidget(self, match_widget, add_to_side):

        if match_widget.side is None:  # middle widget
            segWidget = EnvironmentSegmentWidget(self.inventory,
                                                 parent=self,
                                                 show_full_inventory=self.show_full_inventory,
                                                 side=add_to_side)
            segWidget.segDeleted.connect(self.deleteSeg)
            if add_to_side == 'r':
                layout = self.rhsWidget.layout()
                layout.insertWidget(0, segWidget)
            elif add_to_side == 'l':
                layout = self.lhsWidget.layout()
                layout.insertWidget(len(layout)+1, segWidget)
            layout.update()
            return

        segWidget = EnvironmentSegmentWidget(self.inventory,
                                             parent=self,
                                             show_full_inventory=self.show_full_inventory,
                                             side=match_widget.side)
        segWidget.segDeleted.connect(self.deleteSeg)
        if match_widget.side == 'r':
            layout = self.rhsWidget.layout()
        elif match_widget.side == 'l':
            layout = self.lhsWidget.layout()

        widgets = list()
        for ind in range(layout.count()):
            if layout.itemAt(ind).widget() == match_widget:
                if add_to_side == 'l':
                    widgets.append(segWidget)
                    widgets.append(layout.itemAt(ind).widget())
                elif add_to_side == 'r':
                    widgets.append(layout.itemAt(ind).widget())
                    widgets.append(segWidget)
            else:
                widgets.append(layout.itemAt(ind).widget())

        for i, widget in enumerate(widgets):
            layout.insertWidget(i, widget)
        layout.update()

    @Slot(list) #connected to EnvironmentSegmentWidget.segDeleted()
    def deleteSeg(self, arg):
        segWidget = arg[0]
        if segWidget.side == 'r':
            layout = self.rhsWidget.layout()
        elif segWidget.side == 'l':
            layout = self.lhsWidget.layout()
        for ind in reversed(range(layout.count())):
            if layout.itemAt(ind) == segWidget:
                layout.removeAt(ind)
                break
        segWidget.deleteLater()

    def addLhs(self):
        segWidget = EnvironmentSegmentWidget(self.inventory, parent=self,
                                             show_full_inventory=self.show_full_inventory, side='l')
        self.lhsWidget.layout().insertWidget(0, segWidget)
        segWidget.segDeleted.connect(self.deleteSeg)
        return segWidget

    def addRhs(self):
        segWidget = EnvironmentSegmentWidget(self.inventory, parent=self,
                                             show_full_inventory=self.show_full_inventory, side='r')
        self.rhsWidget.layout().addWidget(segWidget)
        segWidget.segDeleted.connect(self.deleteSeg)
        return segWidget

    def value(self):
        lhsZeroPositions = list()
        rhsZeroPositions = list()
        lhs = []
        for ind in range(self.lhsWidget.layout().count()):
            wid = self.lhsWidget.layout().itemAt(ind).widget()
            lhs.append(wid.value())
            if wid.allowZeroMatch:
                lhsZeroPositions.append(ind)
        rhs = []
        for ind in range(self.rhsWidget.layout().count()):
            wid = self.rhsWidget.layout().itemAt(ind).widget()
            rhs.append(wid.value())
            if wid.allowZeroMatch:
                rhsZeroPositions.append(ind)
        middle = self.middleWidget.value()

        return EnvironmentFilter(middle, lhs, rhs, zeroPositions=(lhsZeroPositions, rhsZeroPositions))

    def displayValue(self):
        lhs = list()
        rhs = list()

        for ind in range(self.lhsWidget.layout().count()):
            wid = self.lhsWidget.layout().itemAt(ind).widget()
            lhs.append(wid.displayValue())
        lhs = ','.join(lhs) if lhs else ''

        for ind in range(self.rhsWidget.layout().count()):
            wid = self.rhsWidget.layout().itemAt(ind).widget()
            rhs.append(wid.displayValue())
        rhs = ','.join(rhs) if rhs else ''

        return '{}_{}'.format(lhs, rhs)


class SyllableConstructDialog(QDialog):
    def __init__(self, inventory, parent=None,
                 preselected_onset=dict(),
                 preselected_nucleus=dict(),
                 preselected_coda=dict(),
                 preselected_stress=set(),
                 preselected_tone=set()):
        QDialog.__init__(self, parent)

        self.setWindowTitle('Construct syllables')

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        layout = QHBoxLayout()
        self.syllWidget = SyllableConstructWidget(inventory, parent=self,
                                                  preselected_onset=preselected_onset,
                                                  preselected_nucleus=preselected_nucleus,
                                                  preselected_coda=preselected_coda)
        layout.addWidget(self.syllWidget)

        optionFrame = QGroupBox('Options')
        optionLayout = QVBoxLayout()
        optionFrame.setLayout(optionLayout)

        self.stressWidget = StressWidget(inventory, parent=self, preselected_stress=preselected_stress)
        optionLayout.addWidget(self.stressWidget)

        self.toneWidget = ToneWidget(inventory, parent=self, preselected_tone=preselected_tone)
        optionLayout.addWidget(self.toneWidget)

        layout.addWidget(optionFrame)
        mainLayout.addLayout(layout)

        acFrame = QFrame()
        acLayout = QHBoxLayout()
        acFrame.setLayout(acLayout)
        self.acceptButton = QPushButton('Ok')
        self.cancelButton = QPushButton('Cancel')
        acLayout.addWidget(self.acceptButton, alignment=Qt.AlignLeft)
        acLayout.addWidget(self.cancelButton, alignment=Qt.AlignLeft)
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        mainLayout.addWidget(acFrame, alignment=Qt.AlignCenter)

    def value(self):
        output = dict()

        output['stress'] = self.stressWidget.value()
        output['tone'] = self.toneWidget.value()
        syllable_info = self.syllWidget.value()
        output.update(syllable_info)

        return output


class SyllableConstructWidget(QGroupBox):
    #sylCopied = Signal(list)

    def __init__(self, inventory, parent=None, show_full_inventory=False,
                 preselected_onset=dict(),
                 preselected_nucleus=dict(),
                 preselected_coda=dict()):
        QGroupBox.__init__(self, 'Syllable', parent)
        self.parent = parent
        self.inventory = inventory
        self.show_full_inventory = show_full_inventory

        layout = QHBoxLayout()

        # onset part
        onsetGroup = QGroupBox('Onset')
        globalOnsetLayout = QVBoxLayout()
        onsetGroup.setLayout(globalOnsetLayout)

        self.onsetSearchType = SearchTypeWidget(parent=onsetGroup,
                                                preselected_type=preselected_onset['search_type'])

        globalOnsetLayout.addWidget(self.onsetSearchType)

        onsetBottomLayout = QHBoxLayout()
        self.onsetWidget = QWidget()
        self.onsetLayout = QHBoxLayout()
        self.onsetWidget.setLayout(self.onsetLayout)


        for seg_dict in preselected_onset['contents']:
            segWidget = SyllableSegmentWidget(self.inventory, "onsets", parent=self, root=False,
                                              show_full_inventory=self.show_full_inventory,
                                              preselected_segments=seg_dict['segments'],
                                              preselected_features=seg_dict['features'],
                                              preselected_negative=seg_dict['negative'])
            self.onsetWidget.layout().addWidget(segWidget)
            segWidget.segDeleted.connect(self.deleteSeg)

        self.onsetAddNew = QPushButton('+')
        self.onsetAddNew.clicked.connect(self.addOnset)
        self.onsetLabel = QLabel()

        onsetBottomLayout.addWidget(self.onsetAddNew)
        onsetBottomLayout.addWidget(self.onsetWidget)
        onsetBottomLayout.addWidget(self.onsetLabel)
        globalOnsetLayout.addLayout(onsetBottomLayout)

        # coda part
        codaGroup = QGroupBox('Coda')
        globalCodaLayout = QVBoxLayout()
        codaGroup.setLayout(globalCodaLayout)

        self.codaSearchType = SearchTypeWidget(parent=codaGroup,
                                               preselected_type=preselected_coda['search_type'])
        globalCodaLayout.addWidget(self.codaSearchType)

        codaBottomLayout = QHBoxLayout()
        self.codaWidget = QWidget()
        self.codaLayout = QHBoxLayout()
        self.codaWidget.setLayout(self.codaLayout)

        for seg_dict in preselected_coda['contents']:
            segWidget = SyllableSegmentWidget(self.inventory, "codas", parent=self, root=False,
                                              show_full_inventory=self.show_full_inventory,
                                              preselected_segments=seg_dict['segments'],
                                              preselected_features=seg_dict['features'],
                                              preselected_negative=seg_dict['negative'])
            self.codaWidget.layout().addWidget(segWidget)
            segWidget.segDeleted.connect(self.deleteSeg)

        self.codaAddNew = QPushButton('+')
        self.codaAddNew.clicked.connect(self.addCoda)
        self.codaLabel = QLabel()

        codaBottomLayout.addWidget(self.codaLabel)
        codaBottomLayout.addWidget(self.codaWidget)
        codaBottomLayout.addWidget(self.codaAddNew)
        globalCodaLayout.addLayout(codaBottomLayout)

        # nucleus part
        nucleusGroup = QGroupBox('Nucleus')
        globalNucleusLayout = QVBoxLayout()
        nucleusGroup.setLayout(globalNucleusLayout)

        self.nucleusSearchType = SearchTypeWidget(parent=nucleusGroup,
                                                  preselected_type=preselected_nucleus['search_type'])
        globalNucleusLayout.addWidget(self.nucleusSearchType)

        bottomLayout = QHBoxLayout()
        self.nucleusWidget = QWidget()
        self.nucleusLayout = QHBoxLayout()
        self.nucleusWidget.setLayout(self.nucleusLayout)

        if preselected_nucleus['contents']:
            self.nucleus = SyllableSegmentWidget(self.inventory,
                                                "nuclei",
                                                parent=self,
                                                root=True,
                                                show_full_inventory=show_full_inventory,
                                                preselected_segments=preselected_nucleus['contents'][0]['segments'],
                                                preselected_features=preselected_nucleus['contents'][0]['features'],
                                                preselected_negative=preselected_nucleus['contents'][0]['negative'])
        else:
            self.nucleus = SyllableSegmentWidget(self.inventory,
                                                 "nuclei",
                                                 parent=self,
                                                 root=True)

        self.nucleusLayout.addWidget(self.nucleus)
        bottomLayout.addWidget(self.nucleusWidget)
        globalNucleusLayout.addLayout(bottomLayout)

        layout.addWidget(onsetGroup)
        layout.addWidget(nucleusGroup)
        layout.addWidget(codaGroup)
        layout.addStretch()
        self.setLayout(layout)
        self.setZeroSymbol()


    def setZeroSymbol(self):
        if self.onsetLayout.count() == 0:
            self.onsetLabel.setText('\u2205')
        else:
            self.onsetLabel.setText('')

        if self.codaLayout.count() == 0:
            self.codaLabel.setText('\u2205')
        else:
            self.codaLabel.setText('')

    def addOnset(self):
        segWidget = SyllableSegmentWidget(self.inventory, "onsets", parent=self, root=False, show_full_inventory=self.show_full_inventory)
        self.onsetWidget.layout().insertWidget(0, segWidget)
        segWidget.segDeleted.connect(self.deleteSeg)
        self.setZeroSymbol()
        return segWidget

    def addCoda(self):
        segWidget = SyllableSegmentWidget(self.inventory, "codas", parent=self, root=False, show_full_inventory=self.show_full_inventory)
        self.codaWidget.layout().addWidget(segWidget)
        segWidget.segDeleted.connect(self.deleteSeg)
        self.setZeroSymbol()
        return segWidget

    @Slot(list)  # connected to SyllableWidget.segDeleted()
    def deleteSeg(self, arg):
        segWidget = arg[0]
        if segWidget.constituent == "codas":
            layout = self.codaWidget.layout()
        elif segWidget.constituent == 'onsets':
            layout = self.onsetWidget.layout()

        for ind in reversed(range(layout.count())):
            if layout.itemAt(ind).widget() == segWidget:
                layout.removeWidget(segWidget)
                break
        segWidget.deleteLater()
        self.setZeroSymbol()

    def value(self):
        output = {'onset': dict(),
                  'nucleus': dict(),
                  'coda': dict()}

        output['onset']['search_type'] = self.onsetSearchType.value()
        output['nucleus']['search_type'] = self.nucleusSearchType.value()
        output['coda']['search_type'] = self.codaSearchType.value()

        output['onset']['contents'] = list()
        for i in range(self.onsetLayout.count()):
            segWidget = self.onsetLayout.itemAt(i).widget()
            output['onset']['contents'].append(segWidget.value())

        output['nucleus']['contents'] = list()
        for k in range(self.nucleusLayout.count()):
            segWidget = self.nucleusLayout.itemAt(k).widget()
            output['nucleus']['contents'].append(segWidget.value())

        output['coda']['contents'] = list()
        for j in range(self.codaLayout.count()):
            segWidget = self.codaLayout.itemAt(j).widget()
            output['coda']['contents'].append(segWidget.value())

        return output

    def displayValue(self):
        pass

        
class SearchTypeWidget(QGroupBox):
    def __init__(self, parent=None, preselected_type=''):
        QGroupBox.__init__(self, 'Search type', parent)

        layout = QVBoxLayout()
        self.typeSelect = QComboBox()

        for search_type in ['Exactly matches', 'Minimally contains', 'Starts with', 'Ends with']:
            self.typeSelect.addItem(search_type)

        layout.addWidget(self.typeSelect)

        index = self.typeSelect.findText('Minimally contains')
        self.typeSelect.setCurrentIndex(index)

        if preselected_type:
            preselected_index = self.typeSelect.findText(preselected_type)
            self.typeSelect.setCurrentIndex(preselected_index)

        self.setLayout(layout)

    def value(self):
        return str(self.typeSelect.currentText())


class StressWidget(QGroupBox):
    def __init__(self, inventory, parent=None, preselected_stress=set()):
        QGroupBox.__init__(self, 'Stress', parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.options = list(inventory.stress_types.keys()) + ['None']

        for stress in self.options:
            setattr(self, stress, QCheckBox(stress))
            self.layout.addWidget(getattr(self, stress))
            if stress in preselected_stress:
                getattr(self, stress).setChecked(True)

        # If there is no stress, then disable this widget
        if len(inventory.stress_types.keys()) == 0:
            self.setEnabled(False)

    def value(self):
        if not self.isEnabled():
            return set()

        selected = set()
        for stress in self.options:
            button = getattr(self, stress)
            if button.isChecked():
                selected.add(button.text())

        return selected

        
class ToneWidget(QGroupBox):
    def __init__(self, inventory, parent=None, preselected_tone=set()):
        QGroupBox.__init__(self, 'Tone', parent)
        self.inventory = inventory

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.options = list(inventory.tone_types.keys()) + ['None']

        for tone in self.options:
            setattr(self, tone, QCheckBox(tone))
            self.layout.addWidget(getattr(self, tone))
            if tone in preselected_tone:
                getattr(self, tone).setChecked(True)

        # If there is no stress, then disable this widget
        if len(inventory.tone_types.keys()) == 0:
            self.setEnabled(False)

    def value(self):
        if not self.isEnabled():
            return set()

        selected = set()
        for tone in self.options:
            button = getattr(self, tone)
            if button.isChecked():
                selected.add(button.text())

        return selected


class SyllableSegmentWidget(QWidget):
    segDeleted = Signal(list)

    def __init__(self,
                 inventory,
                 constituent,
                 parent=None,
                 root=False,
                 show_full_inventory=False,
                 preselected_segments=set(),
                 preselected_features=set(),
                 preselected_negative=False):
        QWidget.__init__(self, parent)
        self.inventory = inventory
        self.constituent = constituent
        self.segments = preselected_segments
        self.features = preselected_features
        self.parent_ = parent
        self.show_full_inventory = show_full_inventory
        self.root = root
        self.negative = preselected_negative

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.mainLabel = QPushButton("{}")
        self.mainLabel.setStyleSheet("padding: 4px")
        layout.addWidget(self.mainLabel)

        self.menu = QMenu(self)
        segmentAct = QAction("Add segments", self, triggered=self.selectSegments)
        featureAct = QAction("Add features", self, triggered=self.selectFeatures)
        clearAct = QAction("Clear selection", self, triggered=self.clearSelection)
        matchAnythingAct = QAction("Match single wildcard", self, triggered=self.addArbitrary)
        self.negAct = QAction("Set negative", self, checkable=True, triggered=self.setNegative)
        if self.negative:
            self.negAct.setChecked(True)
        self.menu.addAction(segmentAct)
        self.menu.addAction(featureAct)
        self.menu.addAction(clearAct)
        self.menu.addAction(matchAnythingAct)
        self.menu.addAction(self.negAct)
        if not self.root:
            deleteAct = QAction("Delete", self, triggered=self.deleteSelection)
            self.menu.addAction(deleteAct)

        self.mainLabel.setMenu(self.menu)
        self.updateLabel()

    def setNegative(self):
        self.negative = self.negAct.isChecked()

    def addArbitrary(self):
        self.segments = set(self.inventory.segs.keys()) - {'#'}  # Add all segs except for the boundary symbol #
        self.updateLabel()

    def clearSelection(self):
        self.segments = set()
        self.features = set()
        self.negative = False
        self.updateLabel()

    def deleteSelection(self):
        self.segDeleted.emit([self])

    def updateLabel(self):
        labelText = self.generateDisplayText()
        if not labelText:
            labelText = '{}'
        labelText = '{}'.format(labelText)
        self.mainLabel.setText(labelText)

    def generateDisplayText(self):
        displayList = list()
        if len(self.segments) == len(self.inventory.segs.keys()) - 1:  # exclude '#'
            if self.show_full_inventory:
                displayList = ', '.join(self.segments)
            else:
                displayList = '{*}'
        else:
            displayList.extend(self.segments)
            displayList.extend(self.features)
            displayList = ', '.join(displayList)
            displayList = '{{{}}}'.format(displayList)

        return displayList

    def selectSegments(self):
        dialog = SegmentSelectDialog(self.inventory, self.segments, self, start_pressed=self.segments)
        if dialog.exec_():
            self.segments = set(dialog.value())
            self.updateLabel()

    def selectFeatures(self):
        dialog = SegmentSelectDialog(self.inventory, self.segments, self, use_features=True)
        if dialog.exec_():
            self.features = set(dialog.value())
            self.updateLabel()

    def value(self):
        # {'segments': ('p', 't', 'k'),
        # 'features': ('+syllabic')}

        output = dict()
        output['segments'] = self.segments
        output['features'] = self.features
        output['negative'] = self.negative

        return output

    def displayValue(self):
        return self.generateDisplayText()

    def getData(self):
        pass
        """
        attrs = ['inventory', 'segments', 'features', 'inventory', 'middle', 'enabled',
                 'show_full_inventory', 'side', 'allowZeroMatch']
        return {attr:getattr(self,attr) for attr in attrs}
        """

    def loadData(self, data):
        pass
        """
        for k, v in data.items(): #see the getData() function above for details
            setattr(self, k, v)
        """


class SyllableWidget(QWidget):
    segDeleted = Signal(list)

    def __init__(self, inventory, parent=None, middle=False, show_full_inventory=False, side=None, preset=False):
        QWidget.__init__(self, parent)
        self.inventory = inventory

        # Crucial data
        self.onset = {'search_type': '', 'contents': []}
        self.nucleus = {'search_type': '', 'contents': []}
        self.coda = {'search_type': '', 'contents': []}
        self.stress = set()
        self.tone = set()
        self.nonSeg = set()

        self.parent = parent
        self.show_full_inventory = show_full_inventory
        self.side = side
        self.middle = middle

        layout = QVBoxLayout()

        self.specification = QFormLayout()
        self.onsetLabel = QLabel()
        self.nucleusLabel = QLabel()
        self.codaLabel = QLabel()
        self.stressLabel = QLabel()
        self.toneLabel = QLabel()
        self.specification.addRow('Onset:', self.onsetLabel)
        self.specification.addRow('Nucleus:', self.nucleusLabel)
        self.specification.addRow('Coda:', self.codaLabel)
        self.specification.addRow('Stress:', self.stressLabel)
        self.specification.addRow('Tone:', self.toneLabel)

        if self.middle:
            self.specification.addRow('POSITION', QLabel('MIDDLE'))
        layout.addLayout(self.specification)

        self.mainLabel = QPushButton('Edit')
        #self.mainLabel.setStyleSheet("padding: 4px")
        layout.addWidget(self.mainLabel)

        self.setLayout(layout)

        self.menu = QMenu(self)
        unspecifiedSyllableAct = QAction('Add an unspecified syllable', self, triggered=self.addUnspecifiedSyllable)
        syllableAct = QAction('Construct the syllable', self, triggered=self.constructSyllable)
        clearAct = QAction('Clear selection', self, triggered=self.clearSelection)
        self.menu.addAction(unspecifiedSyllableAct)
        self.menu.addAction(syllableAct)
        self.menu.addAction(clearAct)

        if not self.middle:
            nonSegSelectMenu = self.menu.addMenu('Add non-segment symbol')
            for symbol in self.inventory.non_segment_symbols:
                nonSegSelectMenu.addAction(QAction(symbol, self, triggered=self.addNonSegSymbol))
            deleteAct = QAction('Delete', self, triggered=self.deleteSelection)
            self.menu.addAction(deleteAct)
        self.mainLabel.setMenu(self.menu)

        addNewPosMenu = self.menu.addMenu('Add new environment position')
        addToLeftAct = QAction('To the left', self, triggered=self.addToLeft)
        addToRightAct = QAction('To the right', self, triggered=self.addToRight)
        addNewPosMenu.addAction(addToLeftAct)
        addNewPosMenu.addAction(addToRightAct)

        self.updateLabel()

        if preset:
            self.onset = preset.onset
            self.nucleus = preset.nucleus
            self.coda = preset.coda
            self.stress = preset.stress
            self.tone = preset.tone
            self.nonSeg = preset.nonSeg
            self.updateLabel()

    def addToLeft(self):
        self.parent.insertSegWidget(self, 'l')

    def addToRight(self):
        self.parent.insertSegWidget(self, 'r')

    def addNonSegSymbol(self):
        self.nonSeg.add(self.sender().text())
        self.onset = {'search_type': '', 'contents': []}
        self.nucleus = {'search_type': '', 'contents': []}
        self.coda = {'search_type': '', 'contents': []}
        self.stress = set()
        self.tone = set()
        self.updateLabel()

    def clearSelection(self):
        self.onset = {'search_type': '', 'contents': []}
        self.nucleus = {'search_type': '', 'contents': []}
        self.coda = {'search_type': '', 'contents': []}
        self.stress = set()
        self.tone = set()
        self.nonSeg = set()

        self.mainLabel.setText('Edit')
        self.updateLabel()

    def deleteSelection(self):
        self.segDeleted.emit([self])  # connected to SyllableConstructionWidget.deleteSeg()

    def updateLabel(self):
        self.generateDisplayText()
        if (self.nonSeg == set() and self.onset == {'contents': [], 'search_type': 'Minimally contains'} and
                self.nucleus == {'contents': [], 'search_type': 'Minimally contains'} and
                self.coda == {'contents': [], 'search_type': 'Minimally contains'} and
                self.stress == set(list(self.inventory.stress_types.keys()) + ['None']) and
                self.tone == set(list(self.inventory.tone_types.keys()) + ['None'])):
            label = '{' + '\u03C3' + '}'
            self.mainLabel.setText(label)

    def generateColorText(self, slot, neg_color='darkRed', pos_color='darkGreen'):
        if len(slot['segments']) == len(self.inventory.segs.keys()) - 1:  # exclude '#'
            if self.show_full_inventory:
                display_text = '{' + ', '.join(self.segments) + '}'
            else:
                display_text = '{*}'
        else:
            display_list = list()
            display_list.extend(slot['segments'])
            display_list.extend(slot['features'])
            display_text = '{' + ', '.join(display_list) + '}'

        if slot['negative']:
            display_text = '<font color=\"' + neg_color + '\">' + display_text + '</font>'
        else:
            display_text = '<font color=\"' + pos_color + '\">' + display_text + '</font>'

        return display_text

    def generateDisplayText(self):

        display_onset = ''
        for slot in self.onset['contents']:
            display_text = self.generateColorText(slot)
            display_onset += display_text

        self.onsetLabel.setText(display_onset)
        if self.onset['search_type'] == 'Exactly matches':
            self.onsetLabel.setStyleSheet('background:transparent')
        elif self.onset['search_type'] == 'Minimally contains':
            self.onsetLabel.setStyleSheet('background:white')
        elif self.onset['search_type'] == 'Starts with':
            self.onsetLabel.setStyleSheet('background:lightgreen')
        elif self.onset['search_type'] == 'Ends with':
            self.onsetLabel.setStyleSheet('background:#FAAFBE')

        display_nucleus = ''
        for slot in self.nucleus['contents']:
            display_text = self.generateColorText(slot)
            display_nucleus += display_text

        self.nucleusLabel.setText(display_nucleus)
        if self.nucleus['search_type'] == 'Exactly matches':
            self.nucleusLabel.setStyleSheet('background:transparent')
        elif self.nucleus['search_type'] == 'Minimally contains':
            self.nucleusLabel.setStyleSheet('background:white')
        elif self.nucleus['search_type'] == 'Starts with':
            self.nucleusLabel.setStyleSheet('background:lightgreen')
        elif self.nucleus['search_type'] == 'Ends with':
            self.nucleusLabel.setStyleSheet('background:#FAAFBE')

        display_coda = ''
        for slot in self.coda['contents']:
            display_text = self.generateColorText(slot)
            display_coda += display_text

        self.codaLabel.setText(display_coda)
        if self.coda['search_type'] == 'Exactly matches':
            self.codaLabel.setStyleSheet('background:transparent')
        elif self.coda['search_type'] == 'Minimally contains':
            self.codaLabel.setStyleSheet('background:white')
        elif self.coda['search_type'] == 'Starts with':
            self.codaLabel.setStyleSheet('background:lightgreen')
        elif self.coda['search_type'] == 'Ends with':
            self.codaLabel.setStyleSheet('background:#FAAFBE')

        display_stress = '{' + ', '.join(self.stress) + '}'
        display_tone = '{' + ', '.join(self.tone) + '}'

        self.stressLabel.setText(display_stress)
        self.toneLabel.setText(display_tone)

        if self.nonSeg:
            label = '{' + ', '.join(self.nonSeg) + '}'
            self.mainLabel.setText(label)

    def addUnspecifiedSyllable(self):
        self.nonSeg = set()
        self.onset = {'contents': [], 'search_type': 'Minimally contains'}
        self.nucleus = {'contents': [], 'search_type': 'Minimally contains'}
        self.coda = {'contents': [], 'search_type': 'Minimally contains'}
        self.stress = set(list(self.inventory.stress_types.keys()) + ['None'])
        self.tone = set(list(self.inventory.tone_types.keys()) + ['None'])

        label = '{' + '\u03C3' + '}'
        self.mainLabel.setText(label)
        self.updateLabel()

    def constructSyllable(self):
        dialog = SyllableConstructDialog(self.inventory, parent=self,
                                         preselected_onset=self.onset,
                                         preselected_nucleus=self.nucleus,
                                         preselected_coda=self.coda,
                                         preselected_stress=self.stress,
                                         preselected_tone=self.tone)
        if dialog.exec_():  # Ok pressed
            result = dialog.value()
            self.onset = result['onset']
            #print('Onset =')
            #pprint(self.onset)
            self.nucleus = result['nucleus']
            #print('Nuclues =')
            #pprint(self.nucleus)
            self.coda = result['coda']
            #print('Coda =')
            #pprint(self.coda)
            self.stress = result['stress']
            #print('Stress =')
            #pprint(self.stress)
            self.tone = result['tone']
            #print('Tone =')
            #pprint(self.tone)
            self.updateLabel()

    def extract_unit_info(self, unit):
        segs = unit['segments']
        if unit['features']:
            more_segs = self.inventory.features_to_segments(list(unit['features']))
            segs = segs.union(more_segs)

        if unit['negative']:
            all_segs = set(self.inventory.segs.keys()) - {'#'}
            segs = all_segs - segs

        return segs

    def value(self):
        output = {'onset': {'contents': list(), 'search_type': self.onset['search_type']},
                  'nucleus': {'contents': list(), 'search_type': self.nucleus['search_type']},
                  'coda': {'contents': list(), 'search_type': self.coda['search_type']}}

        for unit in self.onset['contents']:
            output['onset']['contents'].append(self.extract_unit_info(unit))

        for unit in self.coda['contents']:
            output['coda']['contents'].append(self.extract_unit_info(unit))

        for unit in self.nucleus['contents']:
            output['nucleus']['contents'].append(self.extract_unit_info(unit))

        output['stress'] = self.stress
        output['tone'] = self.tone
        output['nonsegs'] = self.nonSeg

        return output

    def generateSlotText(self, slot):
        if len(slot['segments']) == len(self.inventory.segs.keys()) - 1:  # exclude '#'
            if self.show_full_inventory:
                display_text = '(' + ','.join(self.segments) + ')'
            else:
                display_text = '(*)'
        else:
            display_list = list()
            display_list.extend(slot['segments'])
            display_list.extend(slot['features'])
            display_text = '(' + ','.join(display_list) + ')'

        return display_text

    def displayValue(self):
        if self.nonSeg:
            text = '{' + ', '.join(self.nonSeg) + '}'
            return text
        elif self.mainLabel.text() == '{\u03C3}':
            return '\u03C3'
        else:
            onset = ''
            for slot in self.onset['contents']:
                text = self.generateSlotText(slot)
                onset += text

            nucleus = ''
            for slot in self.nucleus['contents']:
                text = self.generateSlotText(slot)
                nucleus += text

            coda = ''
            for slot in self.coda['contents']:
                text = self.generateSlotText(slot)
                coda += text
            return '{' + onset + nucleus + coda + '}'

    def getData(self):
        attrs = ['inventory', 'onset', 'nucleus', 'coda', 'stress', 'tone', 'nonSeg',
                 'middle', 'show_full_inventory', 'side']
        return {attr: getattr(self, attr) for attr in attrs}

    def loadData(self, data):
        for k, v in data.items():  # see the getData() function above for details
            setattr(self, k, v)


class EnvironmentSyllableWidget(QWidget):
    envCopied = Signal(list)

    def __init__(self, inventory, parent=None, middle=True, copy_data=None, show_full_inventory=False):
        QWidget.__init__(self)
        self.inventory = inventory
        self.parent = parent
        self.middle = middle
        self.show_full_inventory = show_full_inventory
        self.envCopied.connect(self.parent.addCopiedEnvironment)
        layout = QHBoxLayout()

        self.lhsAddNew = QPushButton('+')
        self.lhsAddNew.setFixedWidth(50)
        self.lhsAddNew.clicked.connect(self.addLhs)

        self.lhsWidget = QWidget()
        self.lhsLayout = QHBoxLayout()
        self.lhsWidget.setLayout(self.lhsLayout)

        self.rhsAddNew = QPushButton('+')
        self.rhsAddNew.setFixedWidth(50)
        self.rhsAddNew.clicked.connect(self.addRhs)

        self.rhsWidget = QWidget()
        self.rhsLayout = QHBoxLayout()
        self.rhsWidget.setLayout(self.rhsLayout)

        self.middleWidget = SyllableWidget(self.inventory,
                                           parent=self,
                                           middle=True,
                                           show_full_inventory=show_full_inventory)

        self.removeButton = QPushButton('Remove environment')
        self.removeButton.clicked.connect(self.deleteLater)
        self.copyButton = QPushButton('Copy environment')
        self.copyButton.clicked.connect(self.copyEnvironment)

        layout.addWidget(self.lhsAddNew)
        layout.addWidget(self.lhsWidget)
        layout.addWidget(self.middleWidget)
        layout.addWidget(self.rhsWidget)
        layout.addWidget(self.rhsAddNew)

        layout.addStretch()

        optionlayout = QVBoxLayout()

        optionlayout.addWidget(self.removeButton)
        optionlayout.addWidget(self.copyButton)

        layout.addLayout(optionlayout)

        self.setLayout(layout)
        self.sizeHint()

        if copy_data:
            self.loadfromCopy(copy_data)

    def loadfromCopy(self, copy_data):
        self.middleWidget.onset = copy_data.middleWidget.onset
        self.middleWidget.nucleus = copy_data.middleWidget.nucleus
        self.middleWidget.coda = copy_data.middleWidget.coda
        self.middleWidget.stress = copy_data.middleWidget.stress
        self.middleWidget.tone = copy_data.middleWidget.tone
        self.middleWidget.nonSeg = copy_data.middleWidget.nonSeg
        self.middleWidget.mainLabel.setText(copy_data.middleWidget.mainLabel.text())

        for ind in range(copy_data.lhsWidget.layout().count()):
            copy_wid = copy_data.lhsWidget.layout().itemAt(ind).widget()
            wid = SyllableWidget(self.inventory, parent=self, side='l', preset=copy_wid)
            self.lhsWidget.layout().insertWidget(ind, wid)
            wid.segDeleted.connect(self.deleteSeg)
        for ind in range(copy_data.rhsWidget.layout().count()):
            copy_wid = copy_data.rhsWidget.layout().itemAt(ind).widget()
            wid = SyllableWidget(self.inventory, parent=self, side='r', preset=copy_wid)
            self.rhsWidget.layout().insertWidget(ind, wid)
            wid.segDeleted.connect(self.deleteSeg)

    def copyEnvironment(self):
        self.envCopied.emit([self])  # connected to EnvironmentSelectWidget.addCopiedEnvironment()

    def insertSegWidget(self, match_widget, add_to_side):

        if match_widget.side is None:  # middle widget
            segWidget = SyllableWidget(self.inventory,
                                       parent=self,
                                       show_full_inventory=self.show_full_inventory,
                                       side=add_to_side)
            segWidget.segDeleted.connect(self.deleteSeg)
            if add_to_side == 'r':
                layout = self.rhsWidget.layout()
                layout.insertWidget(0, segWidget)
            elif add_to_side == 'l':
                layout = self.lhsWidget.layout()
                layout.insertWidget(len(layout)+1, segWidget)
            layout.update()
            return

        segWidget = SyllableWidget(self.inventory,
                                   parent=self,
                                   show_full_inventory=self.show_full_inventory,
                                   side=match_widget.side)
        segWidget.segDeleted.connect(self.deleteSeg)
        if match_widget.side == 'r':
            layout = self.rhsWidget.layout()
        elif match_widget.side == 'l':
            layout = self.lhsWidget.layout()

        widgets = list()
        for ind in range(layout.count()):
            if layout.itemAt(ind).widget() == match_widget:
                if add_to_side == 'l':
                    widgets.append(segWidget)
                    widgets.append(layout.itemAt(ind).widget())
                elif add_to_side == 'r':
                    widgets.append(layout.itemAt(ind).widget())
                    widgets.append(segWidget)
            else:
                widgets.append(layout.itemAt(ind).widget())

        for i, widget in enumerate(widgets):
            layout.insertWidget(i, widget)
        layout.update()

    @Slot(list)  # connected to SyllableWidget.segDeleted()
    def deleteSeg(self, arg):
        segWidget = arg[0]
        if segWidget.side == 'r':
            layout = self.rhsWidget.layout()
        elif segWidget.side == 'l':
            layout = self.lhsWidget.layout()
        for ind in reversed(range(layout.count())):
            if layout.itemAt(ind) == segWidget:
                layout.removeAt(ind)
                break
        segWidget.deleteLater()

    def addLhs(self):
        segWidget = SyllableWidget(self.inventory,
                                   parent=self,
                                   show_full_inventory=self.show_full_inventory,
                                   side='l')
        self.lhsWidget.layout().insertWidget(0, segWidget)
        segWidget.segDeleted.connect(self.deleteSeg)
        return segWidget

    def addRhs(self):
        segWidget = SyllableWidget(self.inventory,
                                   parent=self,
                                   show_full_inventory=self.show_full_inventory,
                                   side='r')
        self.rhsWidget.layout().addWidget(segWidget)
        segWidget.segDeleted.connect(self.deleteSeg)
        return segWidget

    def value(self):
        lhs = []
        for ind in range(self.lhsWidget.layout().count()):
            wid = self.lhsWidget.layout().itemAt(ind).widget()
            lhs.append(wid.value())

        middle = [self.middleWidget.value()]

        rhs = []
        for ind in range(self.rhsWidget.layout().count()):
            wid = self.rhsWidget.layout().itemAt(ind).widget()
            rhs.append(wid.value())

        return SyllableEnvironmentFilter(self.inventory, middle, lhs=lhs, rhs=rhs)


    def displayValue(self):
        lhs = list()
        rhs = list()

        for ind in range(self.lhsWidget.layout().count()):
            wid = self.lhsWidget.layout().itemAt(ind).widget()
            lhs.append(wid.displayValue())
        lhs = ''.join(lhs) if lhs else ''

        for ind in range(self.rhsWidget.layout().count()):
            wid = self.rhsWidget.layout().itemAt(ind).widget()
            rhs.append(wid.displayValue())
        rhs = ''.join(rhs) if rhs else ''

        return '{}_{}'.format(lhs, rhs)
