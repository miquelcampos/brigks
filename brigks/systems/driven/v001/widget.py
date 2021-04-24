

from Qt.QtWidgets import QLabel, QComboBox, QPushButton, QComboBox, QDoubleSpinBox

from brigks.systems.systemWidget import SystemWidget


class DrivenSystemWidget(SystemWidget):

	def addWidgets(self):
		uiRotationLAY = self.uiTrackedRotationGRP.layout()
		
		for i in xrange(2, self.guide().count("Rail")+1):
			uiLabel = QLabel("Slider {}".format(i))
			
			uiMinRot = self._addQDoubleSpinBox(-180.0, 180.0, 15.0)
			uiMaxRot = self._addQDoubleSpinBox(-180.0, 180.0, 15.0)
			
			uiAxis = QComboBox()
			uiAxis.addItems(["X","Y","Z"])

			uiSelect = QPushButton("Select")
			uiSet = QPushButton("Set")
			
			uiRotationLAY.addWidget(uiLabel, i, 0)
			uiRotationLAY.addWidget(uiMinRot, i, 1)
			uiRotationLAY.addWidget(uiMaxRot, i, 2)
			uiRotationLAY.addWidget(uiAxis, i, 3)
			uiRotationLAY.addWidget(uiSelect, i, 4)
			uiRotationLAY.addWidget(uiSet, i, 5)
			
			self.__dict__["uiMinRot{}".format(i)] = uiMinRot
			self.__dict__["uiMaxRot{}".format(i)] = uiMaxRot
			self.__dict__["uiAxis{}".format(i)] = uiAxis
			self.__dict__["uiSelect{}".format(i)] = uiSelect
			self.__dict__["uiSet{}".format(i)] = uiSet

	def addConnections(self):
		for i in xrange(1, self.guide().count("Rail")+1):
			self.__dict__["uiSet{}".format(i)].clicked.connect(partial(self._setGuide,i))
			self.__dict__["uiSelect{}".format(i)].clicked.connect(partial(self._selectGuide,i))
			
	def _selectGuide(self, idx):
		if not self.access():
			return

		ctl = self.access().controllers("Part{}".format(idx))
		if not ctl:
			ctl = self.access().objects("Part{}".format(idx), usage="Rig")
		if not ctl:
			return

		Scene().setSelection([ctl])

	def _setGuide(self, idx):
		if not self.access():
			return

		# Gather relevant pieces
		ctlMap = dict(Min="Neg",Max="Pos")

		# Figure out which direction from current angle
		slideAttr = self.access().attributes("setup","Slide{}".format(idx))()
		rotToSliderNode = dcc.maya.cast.toPath(slideAttr.source().node())
		currentAngle = cmds.getAttr(rotToSliderNode+".angle")
		if currentAngle > 0:
			direction = "Max"
		else:
			direction = "Min"

		key = "{}{}".format(ctlMap[direction],idx)
		ctl = self.access().controllers("Part{}".format(idx))
		if not ctl:
			ctl = self.access().objects("Part{}".format(idx), usage="Rig")
		if not ctl:
			return

		ref = self.access().objects(key, usage="Rig")
		rail = self.access().objects("Rail{}".format(idx), usage="Rig")
		refGde = self.guide().markers(key)
		railGde = self.guide().markers("Rail{}".format(idx))

		# Set transform of rig piece and guide
		tfm = ctl.transform(world=True)
		ref.setTransform(tfm, world=True)
		# Guide transform must be set based on rest position, not world position
		refGde.setTransform(tfm * rail.transform().inverted() * railGde.transform())

		# Grab current rotation values and set them in the guide and Rig
		cmds.setAttr(rotToSliderNode+".rot{}".format(direction), currentAngle)
		self.__dict__["ui{}Rot{}".format(direction, idx)].setValue(currentAngle)

		# Reset the controller transforms to match the ref
		ctl.resetTransforms()

	def _addQDoubleSpinBox(self, min, max, step):
		spinBox = QDoubleSpinBox()
		spinBox.setMinimum(min)
		spinBox.setMaximum(max)
		spinBox.setSingleStep(step)
		
		return spinBox