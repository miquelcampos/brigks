
from Qt.QtWidgets import QLabel, QComboBox, QDoubleSpinBox, Q

from brigks.systems.systemWidget import SystemWidget


class SliderSystemWidget(SystemWidget):

	def addConnections(self):
		self.uiAddGuideBTN.clicked.connect(self.addGuide)

	def addWidgets(self):
		uiRotationLAY = self.uiTrackedRotationGRP.layout()
		
		for i in xrange(2, self.guide().count("Rail")+1):
			uiLabel = QLabel("Slider %s"%i)
			
			uiMinRot = self._addQDoubleSpinBox(-180.0, 180.0, 15.0)
			uiMaxRot = self._addQDoubleSpinBox(-180.0, 180.0, 15.0)
			
			uiAxis = QComboBox()
			uiAxis.addItems(["X","Y","Z"])
			
			uiRotationLAY.addWidget(uiLabel, i, 0)
			uiRotationLAY.addWidget(uiMinRot, i, 1)
			uiRotationLAY.addWidget(uiMaxRot, i, 2)
			uiRotationLAY.addWidget(uiAxis, i, 3)
			
			self.__dict__["uiMinRot%s"%i] = uiMinRot
			self.__dict__["uiMaxRot%s"%i] = uiMaxRot
			self.__dict__["uiAxis%s"%i] = uiAxis
			
			
	def _addQDoubleSpinBox(self, minimum, maximum, step):
		spinBox = QDoubleSpinBox()
		spinBox.setMinimum(minimum)
		spinBox.setMaximum(maximum)
		spinBox.setSingleStep(step)
		return spinBox

	def addGuide(self):
		count = self.guide().count("Rail")
		index = self.guide().count("Rail")+1
		lastMarker = self.guide().markers("Rail{}".format(count))
		parent = lastMarker.parent()
		position = lastMarker.transform().translation + Vector(0,.1,0)

		rail = self.guide().addMarkerLocation("Rail{}".format(index), parent=parent, position=position, icon="sphere|null", size=1, po=None, ro=None, so=None)
		pos = Vector(1,0,0) * rail.transformNoScale(world=True)
		markerPos = self.guide().addMarkerLocation("Pos%s"%index, rail, pos, "cube", size=rail.size()*.5)
		pos = Vector(-1,0,0) * rail.transformNoScale(world=True)
		markerNeg = self.guide().addMarkerLocation("Neg%s"%index, rail, pos, "cube", size=rail.size()*.5)
			
		markerPos.setDisplay([{"icon":"null"}], replace=False)
		
		centers = [markerPos, rail, markerNeg]
		crv = self.guide().addMarkerDisplayCurve("Crv%s"%index, centers)

		Scene().setSelection([rail])