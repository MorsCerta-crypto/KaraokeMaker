import sys
from os.path import expanduser
from typing import Optional
from PyQt5.QtWidgets import QMainWindow,QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSlider, QLabel, QFileDialog, QAction, QMessageBox, QApplication, qApp
from PyQt5.QtMultimedia import QMediaPlaylist,QMediaPlayer, QMediaMetaData, QMediaContent
from PyQt5.QtCore import QDirIterator, QUrl, Qt

class MusicPlayer(QMainWindow):
	def __init__(self,file:Optional[str]=None):
		super().__init__()
	
		self.currentFile =  file if file else '/'
		self.currentPlaylist = QMediaPlaylist()
		self.player = QMediaPlayer()
		self.userAction = -1			#0- stopped, 1- playing 2-paused
		self.player.mediaStatusChanged.connect(self.qmp_mediaStatusChanged)
		self.player.stateChanged.connect(self.qmp_stateChanged)
		self.player.positionChanged.connect(self.qmp_positionChanged)
		self.player.volumeChanged.connect(self.qmp_volumeChanged)
		self.player.setVolume(60)
		#Add Status bar
		self.statusBar().showMessage('No Media :: %d'%self.player.volume())
		self.homeScreen()
		
	def homeScreen(self):
		#Set title of the MainWindow
		self.setWindowTitle('Music Player')
		
		#Create Menubar
		self.createMenubar()
		
		#Create Toolbar
		self.createToolbar()
		
		#Add info screen
		#infoscreen = self.createInfoScreen()
		
		#Add Control Bar
		controlBar = self.addControls()
		
		#need to add both infoscreen and control bar to the central widget.
		centralWidget = QWidget()
		centralWidget.setLayout(controlBar)
		self.setCentralWidget(centralWidget)
		
		#Set Dimensions of the MainWindow
		self.resize(200,100)
		
		#show everything.
		self.show()
		
	def createMenubar(self):
		menubar = self.menuBar()
		filemenu = menubar.addMenu('File')
		filemenu.addAction(self.fileOpen())
		filemenu.addAction(self.songInfo())
		filemenu.addAction(self.folderOpen())
		filemenu.addAction(self.exitAction())
		
	def createToolbar(self):
		pass
	
	def addControls(self):
		controlArea = QVBoxLayout()		#centralWidget
		seekSliderLayout = QHBoxLayout()
		controls = QHBoxLayout()
		playlistCtrlLayout = QHBoxLayout()
		
		#creating buttons
		playBtn = QPushButton('Play')		#play button
		pauseBtn = QPushButton('Pause')		#pause button
		stopBtn = QPushButton('Stop')		#stop button
		volumeDescBtn = QPushButton('V (-)')#Decrease Volume
		volumeIncBtn = QPushButton('V (+)')	#Increase Volume
		
		#creating playlist controls
		prevBtn = QPushButton('Prev Song')
		nextBtn = QPushButton('Next Song')
		
		#creating seek slider
		seekSlider = QSlider()
		seekSlider.setMinimum(0)
		seekSlider.setMaximum(100)
		seekSlider.setOrientation(Qt.Horizontal)#type:ignore
		seekSlider.setTracking(False)
		seekSlider.sliderMoved.connect(self.seekPosition)
		#seekSlider.valueChanged.connect(self.seekPosition)
		
		seekSliderLabel1 = QLabel('0.00')
		seekSliderLabel2 = QLabel('0.00')
		seekSliderLayout.addWidget(seekSliderLabel1)
		seekSliderLayout.addWidget(seekSlider)
		seekSliderLayout.addWidget(seekSliderLabel2)
		
		#Add handler for each button. Not using the default slots.
		playBtn.clicked.connect(self.playHandler)
		pauseBtn.clicked.connect(self.pauseHandler)
		stopBtn.clicked.connect(self.stopHandler)
		volumeDescBtn.clicked.connect(self.decreaseVolume)
		volumeIncBtn.clicked.connect(self.increaseVolume)
		
		#Adding to the horizontal layout
		controls.addWidget(volumeDescBtn)
		controls.addWidget(playBtn)
		controls.addWidget(pauseBtn)
		controls.addWidget(stopBtn)
		controls.addWidget(volumeIncBtn)
		
		#playlist control button handlers
		prevBtn.clicked.connect(self.prevItemPlaylist)
		nextBtn.clicked.connect(self.nextItemPlaylist)
		playlistCtrlLayout.addWidget(prevBtn)
		playlistCtrlLayout.addWidget(nextBtn)
		
		#Adding to the vertical layout
		controlArea.addLayout(seekSliderLayout)
		controlArea.addLayout(controls)
		controlArea.addLayout(playlistCtrlLayout)
		return controlArea
	
	def playHandler(self, file:Optional[str]):
		self.userAction = 1
		self.statusBar().showMessage('Playing at Volume %d'%self.player.volume())
		if self.player.state() == QMediaPlayer.StoppedState :#type:ignore
			if self.player.mediaStatus() == QMediaPlayer.NoMedia:#type:ignore
                #if file: self.currentFile = file
				self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.currentFile)))
				#print(self.currentPlaylist.mediaCount())
				if self.currentPlaylist.mediaCount() == 0:
					self.openFile()
				if self.currentPlaylist.mediaCount() != 0:
					self.player.setPlaylist(self.currentPlaylist)
			elif self.player.mediaStatus() == QMediaPlayer.LoadedMedia:#type:ignore
				self.player.play()
			elif self.player.mediaStatus() == QMediaPlayer.BufferedMedia:#type:ignore
				self.player.play()
		elif self.player.state() == QMediaPlayer.PlayingState:#type:ignore
			pass
		elif self.player.state() == QMediaPlayer.PausedState:#type:ignore
			self.player.play()
			
	def pauseHandler(self):
		self.userAction = 2
		self.statusBar().showMessage('Paused %s at position %s at Volume %d'%\
			(self.player.metaData(QMediaMetaData.Title),\
				self.centralWidget().layout().itemAt(0).layout().itemAt(0).widget().text(),\
					self.player.volume()))
		self.player.pause()
			
	def stopHandler(self):
		self.userAction = 0
		self.statusBar().showMessage('Stopped at Volume %d'%(self.player.volume()))
		if self.player.state() == QMediaPlayer.PlayingState:#type:ignore
			self.stopState = True
			self.player.stop()
		elif self.player.state() == QMediaPlayer.PausedState:#type:ignore
			self.player.stop()
		elif self.player.state() == QMediaPlayer.StoppedState:#type:ignore
			pass
		
	def qmp_mediaStatusChanged(self):
		if self.player.mediaStatus() == QMediaPlayer.LoadedMedia and self.userAction == 1:#type:ignore
			durationT = self.player.duration()
			self.centralWidget().layout().itemAt(0).layout().itemAt(1).widget().setRange(0,durationT)
			self.centralWidget().layout().itemAt(0).layout().itemAt(2).widget().setText('%d:%02d'%(int(durationT/60000),int((durationT/1000)%60)))
			self.player.play()
			
	def qmp_stateChanged(self):
		if self.player.state() == QMediaPlayer.StoppedState: #type:ignore
			self.player.stop()
			
	def qmp_positionChanged(self, position,senderType=False):
		sliderLayout = self.centralWidget().layout().itemAt(0).layout()
		if senderType == False:
			sliderLayout.itemAt(1).widget().setValue(position)
		#update the text label
		sliderLayout.itemAt(0).widget().setText('%d:%02d'%(int(position/60000),int((position/1000)%60)))
	
	def seekPosition(self, position):
		sender = self.sender()
		if isinstance(sender,QSlider):
			if self.player.isSeekable():
				self.player.setPosition(position)
				
	def qmp_volumeChanged(self):
		msg = self.statusBar().currentMessage()
		msg = msg[:-2] + str(self.player.volume())
		self.statusBar().showMessage(msg)
		
	def increaseVolume(self):
		vol = self.player.volume()
		vol = min(vol+5,100)
		self.player.setVolume(vol)
		
	def decreaseVolume(self):
		vol = self.player.volume()
		vol = max(vol-5,0)
		self.player.setVolume(vol)
	
	def fileOpen(self):
		fileAc = QAction('Open File',self)
		fileAc.setShortcut('Ctrl+O')
		fileAc.setStatusTip('Open File')
		fileAc.triggered.connect(self.openFile)
		return fileAc
		
	def openFile(self):
		fileChoosen = QFileDialog.getOpenFileUrl(self,'Open Music File', QUrl("karaoke-maker/data/"),'Audio (*.mp3 *.wav)','*.mp3 *.wav')
		if fileChoosen != None:
			self.currentPlaylist.addMedia(QMediaContent(fileChoosen[0]))
	
	def folderOpen(self):
		folderAc = QAction('Open Folder',self)
		folderAc.setShortcut('Ctrl+D')
		folderAc.setStatusTip('Open Folder (Will add all the files in the folder) ')
		folderAc.triggered.connect(self.addFiles)
		return folderAc
	
	def addFiles(self):
		folderChoosen = QFileDialog.getExistingDirectory(self,'Open Music Folder', expanduser('~'))
		if folderChoosen != None:
			it = QDirIterator(folderChoosen)
			it.next()
			while it.hasNext():
				if it.fileInfo().isDir() == False and it.filePath() != '.':
					fInfo = it.fileInfo()
					print(it.filePath(),fInfo.suffix())
					if fInfo.suffix() in ('mp3','ogg','wav'):
						print('added file ',fInfo.fileName())
						self.currentPlaylist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
				it.next()
			
	def songInfo(self):
		infoAc = QAction('Info',self)
		infoAc.setShortcut('Ctrl+I')
		infoAc.setStatusTip('Displays Current Song Information')
		infoAc.triggered.connect(self.displaySongInfo)
		return infoAc
	
	def displaySongInfo(self):
		metaDataKeyList = self.player.availableMetaData()
		fullText = '<table class="tftable" border="0">'
		for key in metaDataKeyList:
			value = self.player.metaData(key)
			fullText = fullText + '<tr><td>' + key + '</td><td>' + str(value) + '</td></tr>'
		fullText = fullText + '</table>'
		infoBox = QMessageBox(self)
		infoBox.setWindowTitle('Detailed Song Information')
		infoBox.setTextFormat(Qt.RichText) # type:ignore
		infoBox.setText(fullText)
		infoBox.addButton('OK',QMessageBox.AcceptRole)
		infoBox.show()
	
	def prevItemPlaylist(self):
		self.player.playlist().previous()
	
	def nextItemPlaylist(self):
		self.player.playlist().next()
	
	def exitAction(self):
		exitAc = QAction('&Exit',self)
		exitAc.setShortcut('Ctrl+Q')
		exitAc.setStatusTip('Exit App')
		exitAc.triggered.connect(self.closeEvent)
		return exitAc
	
	def closeEvent(self,event):
		reply = QMessageBox.question(self,'Message','Pres Yes to Close.',QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
		
		if reply == QMessageBox.Yes :
			qApp.quit()
		else :
			try:
				event.ignore()
			except AttributeError:
				pass
			
	
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = MusicPlayer()
	sys.exit(app.exec_())