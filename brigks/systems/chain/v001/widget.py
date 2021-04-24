

from brigks.systems.systemWidget import SystemWidget


class ChainSystemWidget(SystemWidget):

	def addConnections(self):
		self.uiKinematic.currentIndexChanged.connect(self.refresh)
		self.uiDynamic.clicked.connect(self.refresh)
		self.uiStrap.clicked.connect(self.refresh)
		
	def refresh(self):
		self.uiBlend.setEnabled(str(self.uiKinematic.currentText()) == "FK/IK")
		
		self.uiDynamicDefaultWDG.setEnabled(self.uiDynamic.isChecked())

		self.uiStrapDeformers.setEnabled(self.uiStrap.isChecked())
		self.uiStrapDeformersLBL.setEnabled(self.uiStrap.isChecked())
				