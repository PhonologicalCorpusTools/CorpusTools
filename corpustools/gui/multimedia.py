
from .imports import *


class AudioPlayer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent)
        layout = QHBoxLayout()
        if AUDIO_ENABLED:
            self.player = QMediaPlayer()
            self.player.setNotifyInterval(10)
            self.player.positionChanged.connect(self.checkEnd)
            self.player.positionChanged.connect(self.positionChanged)
        self.begin = -1 #in seconds
        self.end = -1
        self.duration = 0


        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)

        self.labelDuration = QLabel()
        self.slider.sliderMoved.connect(self.seek)
        layout.addWidget(self.slider)
        layout.addWidget(self.labelDuration)
        self.setupActions()

        self.playbar = QToolBar()

        self.playbar.addAction(self.playStopAction)
        self.playbar.addAction(self.stopAction)
        layout.addWidget(self.playbar, alignment=Qt.AlignHCenter)
        self.setLayout(layout)


    def seek(self, milliseconds):
        return
        self.player.setPosition(self.begin+milliseconds)

    def playStopAudio(self):
        if not AUDIO_ENABLED:
            return
        if self.player.mediaStatus() == QMediaPlayer.NoMedia:
            return
        if self.player.state() == QMediaPlayer.StoppedState:
            self.play()
        elif self.player.state() == QMediaPlayer.PausedState:
            self.play()
        elif self.player.state() == QMediaPlayer.PlayingState:
            self.pause()

    def setupActions(self):
        self.playStopAction = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), self.tr("Play"), self)
        self.playStopAction.setShortcut(Qt.NoModifier + Qt.Key_Space)
        self.playStopAction.setDisabled(False)
        self.playStopAction.triggered.connect(self.playStopAudio)

        self.stopAction = QAction(self.style().standardIcon(QStyle.SP_MediaStop), self.tr("Play"), self)
        self.stopAction.setDisabled(False)
        self.stopAction.triggered.connect(self.stop)

    def setLimits(self,begin = -1, end = -1):
        self.begin = begin * 1000
        self.end = end * 1000
        if self.end > 0:
            self.duration = (self.end - self.begin)
        else:
            self.duration = self.player.duration()
        print(self.duration)
        self.slider.setRange(0, self.duration)
        if not AUDIO_ENABLED:
            return
        if self.begin < 0:
            self.player.setPosition(0)
        else:
            self.player.setPosition(self.begin)


    def positionChanged(self, progress):

        if not self.slider.isSliderDown():
            self.slider.setValue(progress - self.begin)

        self.updateDurationInfo(progress - self.begin)

    def updateDurationInfo(self, currentInfo):
        duration = self.duration
        if currentInfo < 0:
            currentInfo = 0
        if currentInfo or duration:
            currentTime = QTime((currentInfo/3600000)%60, (currentInfo/60000)%60,
                    (currentInfo/1000)%60, (currentInfo)%1000)
            totalTime = QTime((duration/3600000)%60, (duration/60000)%60,
                    (duration/1000)%60, (duration)%1000)

            format = 'hh:mm:ss.zzz' if duration > 3600 else 'mm:ss.zzz'
            tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
        else:
            tStr = ""

        self.labelDuration.setText(tStr)

    def play(self):
        if not AUDIO_ENABLED:
            return
        self.playStopAction.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        if self.player.position() >= self.end or self.player.position() < self.begin:
            self.player.setPosition(self.begin)
        self.player.play()

    def pause(self):
        if not AUDIO_ENABLED:
            return
        self.playStopAction.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
        self.player.pause()

    def stop(self):

        if not AUDIO_ENABLED:
            return
        self.playStopAction.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
        self.player.stop()

    def checkEnd(self, position):
        if self.end > self.begin and position >= self.end:
            self.stop()

    def setAudioFile(self, path):

        if not AUDIO_ENABLED:
            return
        self.path = path
        url = QUrl.fromLocalFile(path)
        self.player.setMedia(QMediaContent(url))
