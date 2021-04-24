

from brigks.systems.systemWidget import SystemWidget


class TwistSystemWidget(SystemWidget):
	
	def addConnections(self):
		self.uiTangent.clicked.connect(self.refresh)
		self.uiParametric.clicked.connect(self.refresh)
		
	def refresh(self):
		self.uiTangentDistance.setEnabled(self.uiTangent.isChecked())
		self.uiPreserveLength.setEnabled(self.uiParametric.isChecked() == False)