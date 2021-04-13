from maya import cmds

from math3d.transformation import TransformationArray
from math3d.vectorN import Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import attributes, compounds


class StretchSystemBuilder(SystemBuilder):

	def createObjects(self):
		# TRANSFORMATION
		normal = self.directions("Root", "z")
		positions = Vector3Array([self.translations("Root"), self.translations("End")])
		ctlTfm = TransformationArray.chain(positions, normal, negativeSide=self.negate(), endTransform=True)

		self.length = self.translations("Root").distance(self.translations("End"))

		# CONTROLLERS
		startBfr = self.createBuffer(None, "Start", ctlTfm[0])
		endBfr = self.createBuffer(None, "End", ctlTfm[1])
		
		if self.settings("addControllers"):
			startCtl = self.createController(startBfr, "Start", ctlTfm[0], "cube", color=self.colorIk())
			attributes.setKeyables(startCtl, constants.tr_attrs)
			
			endCtl = self.createController(endBfr, "End", ctlTfm[1], "cube", color=self.colorIk())
			attributes.setKeyables(endCtl, constants.tr_attrs)
			
			self.centers = [startCtl, endCtl]
		else:
			self.centers = [startBfr, endBfr]

		# Stretch
		self.bone = self.createRig(self.centers[0], "Bone", ctlTfm[0], "cube", po=(self.length*.5,0,0), so=(self.length,1,1))

	def createDeformers(self):
		self.addJoint(self.bone, "Bone")

	#----------------------------------------------------------------------------
	# PROPERTIES 
	def createAttributes(self):
		if self.settings("twist"):
			self.twistBlendAttr = self.createAnimAttr("twistBlend", "float", self.settings("twistBlend"), 0, 1)

		if self.settings("squash"):
			self.squashAttr = [self.createAnimAttr("squash"+s, "float", self.settings("squash"+s), None, None, -1, 1) for s in "yz"]

		if self.settings("stretch"):
			self.stretchBlendAttr = self.createAnimAttr("stretchBlend", "float", self.settings("stretchBlend"), 0, 1)

		self.lengthRatioAttr = self.createAnimAttr("lengthRatio", "float", 1, 0, None)

	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		#Direction
		cns = compounds.aimConstraint("AIM", self.bone, self.centers[1], axis="xy", upMaster=self.centers[0], upVector=(0,0,1))

		# Twist
		if self.settings("twist"):
			pabaCns = compounds.pointAtBlendedAxis(cns, self.centers[0], self.centers[1], blend=self.settings("twistBlend"))
			cmds.connectAttr(self.twistBlendAttr, pabaCns+".blend")

		# length ratio
		if self.settings("stretch") or self.settings("squash"):
			multMatNode = self._createNode("multMatrix", "MultMat")
			cmds.connectAttr(self.centers[1]+".worldMatrix[0]", multMatNode+".matrixIn[0]")
			cmds.connectAttr(self.centers[0]+".worldInverseMatrix[0]", multMatNode+".matrixIn[1]")

			distNode = self._createNode("distanceBetween", "Distance")
			cmds.connectAttr(multMatNode+".matrixSum", distNode+".inMatrix2")

			divNode = self._createNode("multiplyDivide", "LengthRatio")
			cmds.setAttr(divNode+".operation", 2) # Divide
			cmds.connectAttr(distNode+".distance", divNode+".input1X")
			cmds.setAttr(divNode+".input2X", self.length)

			cmds.connectAttr(divNode+".outputX", self.lengthRatioAttr)

		# Scaling
		if self.settings("stretch"):
			negateNode = self._createNode("multiplyDivide", "Negate")
			cmds.setAttr(negateNode+".operation", 1) # Multiply
			cmds.connectAttr(self.stretchBlendAttr, negateNode+".input1X")
			cmds.setAttr(negateNode+".input2X", -1)

			addNode1 = self._createNode("addDoubleLinear", "Add")
			cmds.setAttr(addNode1+".input1", 1)
			cmds.connectAttr(negateNode+".outputX", addNode1+".input2")

			mulNode = self._createNode("multiplyDivide", "Multiply")
			cmds.setAttr(mulNode+".operation", 1) # Multiply
			cmds.connectAttr(self.lengthRatioAttr, mulNode+".input1X")
			cmds.connectAttr(self.stretchBlendAttr, mulNode+".input2X")

			addNode2 = self._createNode("addDoubleLinear", "Add")
			cmds.connectAttr(addNode1+".output", addNode2+".input1")
			cmds.connectAttr(mulNode+".outputX", addNode2+".input2")

			cmds.connectAttr(addNode2+".output", self.bone+".scaleX")

		if self.settings("squash"):
			divNode3 = self._createNode("multiplyDivide", "Divide")
			cmds.setAttr(divNode3+".operation", 2) # Divide
			cmds.setAttr(divNode3+".input1X", 1)
			cmds.connectAttr(self.lengthRatioAttr, divNode3+".input2X")

			powNode = self._createNode("multiplyDivide", "Power")
			cmds.setAttr(powNode+".operation", 3) # Power
			cmds.connectAttr(divNode3+".outputX", powNode+".input1Y")
			cmds.connectAttr(self.squashAttr[0], powNode+".input2Y")
			cmds.connectAttr(divNode3+".outputX", powNode+".input1Z")
			cmds.connectAttr(self.squashAttr[1], powNode+".input2Z")

			cmds.connectAttr(powNode+".outputY", self.bone+".scaleY")
			cmds.connectAttr(powNode+".outputZ", self.bone+".scaleZ")
			
	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		if "Start" in self.connections():
			child = self.getObject("Bfr", "Start")
			self.connections("Start").connect(child)

		if "End" in self.connections():
			child = self.getObject("Bfr", "End")
			self.connections("End").connect(child)
