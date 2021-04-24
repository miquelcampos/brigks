
from Qt.QtWidgets import QLabel, QComboBox, QPushButton, QLineEdit

from brigks.systems.systemWidget import SystemWidget


class PsdSystemWidget(SystemWidget):
	
	def addConnections(self):
		self.uiGrabDrvPoseBTN.clicked.connect(self.grabDrvPose)
		self.uiAddDriverBTN.clicked.connect(self.addGuide)
		self.uiGrabMinBTN.clicked.connect(lambda:self.grabTwistFromRig("Min"))
		self.uiGrabMaxBTN.clicked.connect(lambda:self.grabTwistFromRig("Max"))

		for i in xrange(1, self.guide().count("Driver")+1):
			self.__dict__["uiSelectGuide{}".format(i)].clicked.connect(partial(self.selectGuide,i))
			self.__dict__["uiSelectRig{}".format(i)].clicked.connect(partial(self.selectRig,i))

	def addWidgets(self):
		uiDriverLAY = self.uiDriverWDG.layout()
		
		for i in xrange(1, self.guide().count("Driver")+1):
			uiLabel = QLabel("Driver {}".format(i))
			
			uiDrvName = self._addQLineEditBox("Driver{}".format(i))

			uiInterpType = QComboBox()
			uiInterpType.addItems(["Linear","Smooth","Ease In", "Ease Out"])

			uiSelectGuide = QPushButton("Select Guide")
			uiSelectRig = QPushButton("Select Rig")
			
			uiDriverLAY.addWidget(uiLabel, i, 0)
			uiDriverLAY.addWidget(uiDrvName, i, 1)
			uiDriverLAY.addWidget(uiInterpType, i ,2)
			uiDriverLAY.addWidget(uiSelectGuide, i, 3)
			uiDriverLAY.addWidget(uiSelectRig, i, 4)
			
			self.__dict__["uiDrvName{}".format(i)] = uiDrvName
			self.__dict__["uiInterpType{}".format(i)] = uiInterpType
			self.__dict__["uiSelectGuide{}".format(i)] = uiSelectGuide
			self.__dict__["uiSelectRig{}".format(i)] = uiSelectRig
			
			
	def _addQLineEditBox(self, label):
		lineEdit = QLineEdit()
		lineEdit.setText(label)
		return lineEdit
		
	def grabDrvPose(self):
		if not self.access():
			self.warning("psdDriver System hasn't been built")
			return 
		
		# Set marker transforms to match rig objects
		for item in self.access().objects(localName=None, usage="Rig"):
			part = item.name().split("_")[-1]
			if part not in self.guide().markers().keys():
				continue
			marker = self.guide().markers(part)
			marker.setTransform(item.transform(world=True), world=True, childCompensation=True)

	def grabTwistFromRig(self, minMax):
		if not self.access():
			self.warning("PSDDriver system hasn't been built")
			return

		axis = "XYZ".index(self.guide().parameters("twistAxis"))
		currentValue = self.access().attributes("setup", "OutRot").value()[axis]
		self.__dict__["uiTwist%s"%minMax].setValue(currentValue)

		# set the value back into the rig, if created
		attr = self.access().attributes("setup", "Twist%s"%(minMax))
		if attr:
			attr.setValue(currentValue)

	def addGuide(self):
		guide  = self.guide()

		count = guide.count("Driver")
		index = guide.count("Driver")+1
		root = guide.markers("Root")
		position = root.transform().translation

		driver = guide.addMarkerLocation("Driver{}".format(index), parent=root, position=position, icon="pyramid", size=0.5, po=None, ro=[0,-0,-90], so=None)
		pos = Vector(1,0,0) * driver.transformNoScale(world=True)
		outer = guide.addMarkerLocation("Outer{}".format(index), driver, pos, "sphere", 2, None, None, [0,1,1])
		inner = guide.addMarkerLocation("Inner{}".format(index), outer, pos, "sphere", 2, None, None, [0,1,1])
		trans = inner.transform(world=True)
		trans.setScaling(Vector(1.0,0.5,0.5))
		inner.setTransform(trans, world=True)
		
		driver.setTransform(root.transform(), world=True)


		Scene().setSelection([driver])

	def selectGuide(self, idx):
		guide = self.guide().markers("Driver{}".format(idx))
		Scene().setSelection([guide])

	def selectRig(self, idx):
		if not self.access():
			return

		driver = self.access().objects("Driver{}".format(idx), usage="Rig")
		if not driver:
			return

		Scene().setSelection([driver])
