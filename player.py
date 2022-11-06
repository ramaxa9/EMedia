import datetime
import os.path
import subprocess
import sys

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QDir, QUrl, QSize
from PySide2.QtGui import QGuiApplication
from PySide2.QtMultimedia import QMediaContent, QMediaPlayer
from PySide2.QtMultimediaWidgets import QVideoWidget
from PySide2.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QPushButton, QStyle, QVBoxLayout, QCheckBox, \
    QListWidget, QComboBox, QSlider, QLabel, QAbstractItemView, QSpacerItem, QSizePolicy


#TODO: Crop video
#TODO: Video preview in playlist

class HelpDialog(QtWidgets.QDialog):
    def __init__(self):
        super(HelpDialog, self).__init__()
        self.setWindowTitle("Help")
        self.setMinimumSize(400, 800)
        textarea = QtWidgets.QTextBrowser()
        self.setModal(True)
        author = QLabel("Created by Roman Malashevych")
        layout = QVBoxLayout()
        layout.addWidget(textarea)
        layout.addWidget(author)
        self.setLayout(layout)

        helpText = """
Mouse:
    * Double click - load selected media
    * mouse right click - toggle full-screen (video area only)
            
Keyboard:
    * F - toggle full-screen
    * +(plus) - play/pause
    * R - set video slider to 0
    * N - select next
    * P - select previous
    * 0 to 9 - select item in playlist
    * X - put video output to the next screen
    * Z - put video output to the previous screen
        """

        textarea.setText(helpText)


class ControlsWidget(QtWidgets.QWidget):
    def __init__(self):
        # TODO: Next/Prev buttons
        super(ControlsWidget, self).__init__()
        self.setWindowTitle("EMedia Controls")
        self.move(1, 1)
        self.setMinimumWidth(900)

        mainLayout = QVBoxLayout()

        # self.btnMoveScreen = QPushButton("Move to >>")
        self.btnHelp = QPushButton()
        self.btnHelp.setToolTip("Help")
        # self.btnHelp.setMinimumSize(40, 40)
        # self.btnHelp.setMaximumSize(40, 40)
        self.btnHelp.setIconSize(QSize(30, 30))
        self.btnHelp.setIcon(self.style().standardIcon(QStyle.SP_TitleBarContextHelpButton))
        self.playButton = QPushButton("Play")
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pauseButton = QPushButton("Pause")
        self.pauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.stopButton = QPushButton("Stop")
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.fullScreenButton = QPushButton("Fullscreen")
        self.loop = QComboBox()
        self.loop.addItem("Loop None")
        self.loop.addItem("Loop Current")
        self.loop.addItem("Loop Playlist")
        self.loop.setCurrentIndex(0)
        self.allwaysOnTop = QCheckBox("Keep controls on top of other windows")
        self.playOnSelect = QCheckBox("Play immediately")
        # self.playOnSelect.setChecked(True)
        # self.playOnFullscreen = QCheckBox("Play on Fullscreen pressed")
        self.playAll = QCheckBox("Play all")
        self.playlist = QListWidget()
        self.playlist.setDragEnabled(True)
        self.playlist.setAcceptDrops(True)
        self.playlist.setDragDropMode(QAbstractItemView.InternalMove)
        self.screenSelect = QComboBox()
        self.screenSelect.setToolTip("Select screen")
        self.btnUpdateScreens = QPushButton("Reload screens")
        self.btnUpdateScreens.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.openButton = QPushButton("Add Video")
        self.positionSlider = QSlider()
        self.positionSlider.setOrientation(QtCore.Qt.Horizontal)

        # stylesheet = "font-size: 20pt"
        self.mediaDuration = QLabel("0:00:00")
        self.mediaTimeLeft = QLabel("0:00:00")
        # self.mediaTimeLeft.setStyleSheet(stylesheet)
        self.mediaTimeCounter = QLabel("0:00:00")
        # self.mediaTimeCounter.setStyleSheet(stylesheet)

        self.btnDeleteItem = QPushButton('Delete')
        self.infoLabel = QLabel()
        self.infoLabel.setText("Double click on item to load media")
        self.infoLabel.setStyleSheet("color: blue;")

        self.helpDialog = HelpDialog()

        line0 = QHBoxLayout()
        line1 = QHBoxLayout()
        line2 = QHBoxLayout()
        line3 = QHBoxLayout()
        line4 = QHBoxLayout()
        line5 = QHBoxLayout()

        mainLayout.addLayout(line0)
        mainLayout.addLayout(line1)
        mainLayout.addLayout(line2)
        mainLayout.addLayout(line3)
        mainLayout.addLayout(line4, 1)
        mainLayout.addLayout(line5, 1)

        self.setLayout(mainLayout)

        line0.addWidget(self.openButton)
        line0.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        # line0.addWidget(self.mediaTime, 1, QtCore.Qt.AlignCenter)
        line0.addWidget(self.btnHelp)

        line1.addWidget(self.mediaTimeCounter)
        line1.addWidget(self.positionSlider, QtCore.Qt.AlignCenter)
        line1.addWidget(self.mediaDuration)

        line2.addWidget(self.playButton)
        line2.addWidget(self.pauseButton)
        line2.addWidget(self.stopButton)
        line2.addWidget(self.loop)
        line2.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        # line2.addWidget(self.btnMoveScreen)
        line2.addWidget(self.screenSelect)
        line2.addWidget(self.btnUpdateScreens)
        line2.addWidget(self.fullScreenButton)

        line3.addWidget(self.playOnSelect, 1)
        # line3.addWidget(self.playOnFullscreen)

        line4.addWidget(self.playlist)

        line5.addWidget(self.btnDeleteItem)

        self.btnHelp.clicked.connect(self.helpDialog.show)


class VideoWidget(QtWidgets.QWidget):
    def __init__(self, mediafile: str = None):
        super(VideoWidget, self).__init__()
        self.setWindowTitle("EMedia Player")
        # self.setMinimumSize(600, 400)
        # self.move(200, 200)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.move(0, 0)
        self.setMinimumSize(800, 600)

        self.videoPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.videoWidget = QVideoWidget()

        self.videoPlayer.setVideoOutput(self.videoWidget)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.videoWidget)
        # mainLayout.addWidget(self.controls)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        # centralWidget = QtWidgets.QWidget()
        # self.setCentralWidget(centralWidget)
        # centralWidget.setLayout(mainLayout)
        self.setLayout(mainLayout)

        self.offset = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)


class EMediaPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super(EMediaPlayer, self).__init__()

        self.grabKeyboard()

        self.controls = ControlsWidget()
        self.setCentralWidget(self.controls)
        self.videoScreen = VideoWidget()
        self.videoScreen.show()

        self.setWindowTitle(self.controls.windowTitle())

        self.controls.playButton.clicked.connect(self.play)
        self.controls.pauseButton.clicked.connect(self.pause)
        self.controls.stopButton.clicked.connect(self.stop)
        self.controls.openButton.clicked.connect(self.openFile)
        self.controls.btnUpdateScreens.clicked.connect(self.getScreens)
        self.controls.fullScreenButton.clicked.connect(self.fullScreen)
        self.videoScreen.videoPlayer.stateChanged.connect(self.loopMedia)
        self.controls.screenSelect.currentIndexChanged.connect(self.movePlayer)
        # self.controls.playlist.currentRowChanged.connect(self.selectMedia)
        self.controls.playlist.itemDoubleClicked.connect(self.loadSelected)
        self.controls.btnDeleteItem.clicked.connect(self.deleteItemFromPlaylist)

        self.videoScreen.videoPlayer.mediaStatusChanged.connect(self.mediaLoaded)
        self.videoScreen.videoPlayer.positionChanged.connect(self.positionChanged)
        self.videoScreen.videoPlayer.durationChanged.connect(self.durationChanged)
        self.controls.positionSlider.sliderMoved.connect(self.set_position)
        # self.controls.btnMoveScreen.clicked.connect(self.movePlayer)

        self.getScreens()

    def mediaLoaded(self):
        duration = datetime.timedelta(seconds=round(self.videoScreen.videoPlayer.duration() / 1000))
        self.controls.mediaDuration.setText(str(duration))

    def seekVideo(self, value):
        self.videoScreen.videoPlayer.setPosition(value)

    def closeEvent(self, event):
        if event.spontaneous():
            reply = QtWidgets.QMessageBox.question(
                self, 'QUIT',
                'Do you really want to quit?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                sys.exit()
            else:
                event.ignore()

    def deleteItemFromPlaylist(self):
        # if self.controls.playOnSelect.isChecked():
        #     self.videoScreen.videoPlayer.stop()

        item = self.controls.playlist.currentRow()
        self.controls.playlist.takeItem(item)

    def getScreens(self):
        self.controls.screenSelect.clear()
        screens = QGuiApplication.screens()
        for screen in screens:
            self.controls.screenSelect.addItem(screen.name().split('\\')[-1])
            print(screen.name().split('\\')[-1], screen.geometry())

        if list().count(screens) >= 2:
            setcurrent = 1
        else:
            setcurrent = 0

        self.controls.screenSelect.setCurrentIndex(setcurrent)

    def movePlayer(self):
        self.showNormal()
        screen = self.controls.screenSelect.currentIndex()
        try:
            screenGeometry = QGuiApplication.screens()[screen].geometry()
            print(QGuiApplication.screens()[screen].name())
            self.videoScreen.move(screenGeometry.left(), screenGeometry.top())
        except:
            pass

    def fullScreen(self):
        if self.videoScreen.isMaximized():
            self.videoScreen.showNormal()
        else:
            self.videoScreen.showMaximized()

    def loopMedia(self, status):
        # print(self.videoPlayer.mediaStatus(), status)
        if self.videoScreen.videoPlayer.mediaStatus() == 7:
            if self.controls.loop.currentIndex() == 1:
                print("loop current")
                self.videoScreen.videoPlayer.play()
            elif self.controls.loop.currentIndex() == 2:
                current = self.controls.playlist.currentIndex().row()
                print("loop all", current)
                if self.controls.playlist.count() <= current + 1:
                    print("first item", self.controls.playlist.count(), current)
                    self.controls.playlist.setCurrentRow(0)
                else:
                    print("next item", self.controls.playlist.count(), current)
                    self.controls.playlist.setCurrentRow(self.controls.playlist.currentRow() + 1)

                self.loadSelected()
                self.videoScreen.videoPlayer.play()
            else:
                return

    def loadMedia(self, file):
        self.videoScreen.videoPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file)))

        if self.controls.playOnSelect.isChecked():
            self.play()

    def loadSelected(self):
        file = str(self.controls.playlist.currentItem().text()).split('] ')[2]
        if file:
            self.loadMedia(file)

    def playPause(self):
        if self.videoScreen.videoPlayer.state() == QMediaPlayer.PlayingState:
            self.videoScreen.videoPlayer.pause()
        else:
            self.videoScreen.videoPlayer.play()

    def play(self):
        if self.videoScreen.videoPlayer.state() == QMediaPlayer.PlayingState:
            return
        else:
            self.videoScreen.videoPlayer.play()

    def pause(self):
        if self.videoScreen.videoPlayer.state() == QMediaPlayer.PausedState:
            return
        else:
            self.videoScreen.videoPlayer.pause()

    def stop(self):
        if self.videoScreen.videoPlayer.state() == QMediaPlayer.StoppedState:
            return
        else:
            self.videoScreen.videoPlayer.stop()

    def openFile(self, videofile):
        fileNames = QFileDialog.getOpenFileNames(self, "Open Movie",
                                                  QDir.homePath())

        # if fileNames.count() > 0:
        i = self.controls.playlist.count() + 1
        for file in fileNames[0]:
            if os.path.exists(file):
                result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                         "format=duration", "-of",
                                         "default=noprint_wrappers=1:nokey=1", file],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                duration = round(float(result.stdout))

                duration = datetime.timedelta(seconds=duration)
                # self.controls.playlistItems.append([i, mediaduration, file])
                self.controls.playlist.addItem(f"[{i}] [{duration}] {file}")
            i += 1

                    # self.videoPlayer.setMedia(
                    #     QMediaContent(QUrl.fromLocalFile(fileName)))

    def positionChanged(self, position):
        # mediaduration = round((self.videoScreen.videoPlayer.duration() - position) / 1000)
        # mediaduration = round(position)
        # duration = self.videoScreen.videoPlayer.duration()
        counter = datetime.timedelta(seconds=round(position / 1000))
        # timeleft = datetime.timedelta(seconds=round((duration - position)/1000))
        self.controls.mediaTimeCounter.setText(str(counter))
        # self.controls.mediaTimeLeft.setText(str(timeleft))
        self.controls.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.controls.positionSlider.setRange(0, duration)

    def set_position(self, position):
        self.videoScreen.videoPlayer.setPosition(position)

    def playNext(self):
        current = self.controls.playlist.currentRow()
        count = self.controls.playlist.count()
        prev = current - 1
        next = current + 1

        if next > count - 1:
            return
        else:
            self.controls.playlist.setCurrentRow(next)
            self.loadSelected()

    def playPrev(self):
        current = self.controls.playlist.currentRow()
        count = self.controls.playlist.count()
        prev = current - 1
        next = current + 1

        if prev < 0:
            return
        else:
            self.controls.playlist.setCurrentRow(prev)
            self.loadSelected()

    def keyPressEvent(self, event):
        hotkeys = {
            QtCore.Qt.Key_1: 0,
            QtCore.Qt.Key_2: 1,
            QtCore.Qt.Key_3: 2,
            QtCore.Qt.Key_4: 3,
            QtCore.Qt.Key_5: 4,
            QtCore.Qt.Key_6: 5,
            QtCore.Qt.Key_7: 6,
            QtCore.Qt.Key_8: 7,
            QtCore.Qt.Key_9: 8,
            QtCore.Qt.Key_0: 9,
        }

        if event.key() in hotkeys:
            key = hotkeys[event.key()]
            print(key, self.controls.playlist.count())
            if self.controls.playlist.count() > key:
                self.controls.playlist.setCurrentRow(key)
                self.loadSelected()

        if event.key() == QtCore.Qt.Key_R:
            self.videoScreen.videoPlayer.setPosition(0)

        if event.key() == QtCore.Qt.Key_Plus:
            self.playPause()

        if event.key() == QtCore.Qt.Key_F:
            self.fullScreen()

        if event.key() == QtCore.Qt.Key_Z:
            current = self.controls.screenSelect.currentIndex()
            print(current)
            if current == 0:
                return
            else:
                self.controls.screenSelect.setCurrentIndex(current - 1)
                self.showNormal()
                self.videoScreen.resize(QSize(800, 600))
                self.movePlayer()

        if event.key() == QtCore.Qt.Key_X:
            current = self.controls.screenSelect.currentIndex()
            maxcount = self.controls.screenSelect.count()
            print(current, maxcount)
            if maxcount <= current + 1:
                return
            else:
                self.controls.screenSelect.setCurrentIndex(current + 1)
                self.showNormal()
                self.videoScreen.resize(QSize(800, 600))
                self.movePlayer()

        if event.key() == QtCore.Qt.Key_P:
            self.playPrev()

        if event.key() == QtCore.Qt.Key_N:
            self.playNext()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    videoplayer = EMediaPlayer()
    videoplayer.resize(640, 480)
    videoplayer.show()
    sys.exit(app.exec_())
