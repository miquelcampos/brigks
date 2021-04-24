

from brigks.systems.systemWidget import SystemWidget


class BasicSystemWidget(SystemWidget):

	def addConnections(self):
		self.uiKeyableAllBTN.clicked.connect(lambda:self.keyableAll(True))
		self.uiKeyableNoneBTN.clicked.connect(lambda:self.keyableAll(False))
		self.uiDynamic.clicked.connect(self.refresh)
		
		
	def keyableAll(self, value=True):
		for t in "trs":
			for s in "xyz":
				self.widgets[t+s].setChecked(value)
		
		self.widgets["rotorder"].setChecked(value)		
		self.saveSettings()

	def refresh(self):
		self.uiDynamicDefaultWDG.setEnabled(self.uiDynamic.isChecked())
		
			