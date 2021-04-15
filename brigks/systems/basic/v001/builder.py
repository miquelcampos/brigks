from itertools import izip

from maya import cmds

from math3d.transformation import Transformation

from brigks.utils import constants, attributes, compounds
from brigks.systems.systemBuilder import SystemBuilder

class BasicSystemBuilder(SystemBuilder):

	def createObjects(self):
		self.bfr = []
		self.ctl = []
		parent = None

		color = self.settings("colorIk") if self.settings("useIkColor") else self.settings("colorFk")
		axis = self.sign()+"yz"

		self.jntparent = []
		self.splitParent = []
		for i, tfm in enumerate(self.transforms("Part"), start=1):
		# for i, (t, dy, dz) in enumerate(izip(self.translations("Part"), 
		# 								self.directions("Part", "y"),self.directions("Part", "z"))
		# 											  , start=1):

		# 	tfm = Transformation.lookAt(t, dy, dz, axis, negativeSide=self.negate())

			part = "Part{}".format(i)
			bfr = self.createBuffer(None, part, tfm=tfm)
			self.bfr.append(bfr)

			if self.settings("addControllers"):
				ctl = self.createController(bfr, part, tfm=tfm, icon="cube", color=color)
				self.ctl.append(ctl)	
				attributes.setRotOrder(ctl, self.settings("defaultRotationOrder"))

				keyables = [attr for attr in constants.trs_attrs if self.settings(attr)]
				attributes.setKeyables(ctl, keyables)
				jntparent = ctl
			else:
				jntparent = bfr

			if self.settings("dynamic"):
				harmonic = self.createRig(jntparent, "Harmonic{}".format(i), tfm=tfm)
				jntparent = harmonic

			self.jntparent.append(jntparent)

			if self.settings("splitRotation"):
				splitParent = self.createRig(jntparent, "Split{}".format(i), tfm=tfm)
				self.splitParent.append(splitParent)

	def createJoints(self):
		for i, parent in enumerate(self.jntparent, start=1):
			self.createJoint(parent, i)

		for i, parent in enumerate(self.splitParent, start=1):
			jnt = self.createJoint(parent, "Pos{}".format(i))	
			value = cmds.getAttr(jnt+".radius") *.9
			cmds.setAttr(jnt+".radius", value)

	#----------------------------------------------------------------------------
	# PROPERTIES 
	def createAttributes(self):
		if self.settings("dynamic"):
			self.dynamicAttr = self.createAnimAttr("Dynamic", "bool", self.settings("dynActive"))
			self.globalAmplAttr = self.createAnimAttr("GlobalAmplitude", "float", self.settings("amplitude"), 0, 5)
			self.localAmplAttr = [self.createAnimAttr("LocalAmplitude{}".format(i+1), "float", 1, 0, 10) for i in xrange(self.count("Part"))]

			if self.settings("dynamicAnimatable"):
				self.axisAttr = self.createAnimAttr("Axis", "double3", (self.settings("amplitudeX"), self.settings("amplitudeY"), self.settings("amplitudeZ")))
				self.decayAttr = self.createAnimAttr("Decay", "float", self.settings("decay"), 0, 10)
				self.terminationAttr = self.createAnimAttr("Termination", "float", self.settings("termination"), 0, 1)
				self.frequencyAttr = self.createAnimAttr("Frequency", "float", self.settings("frequency"), 0, 1)

	#----------------------------------------------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		if self.settings("splitRotation"):
			for i, bfr in enumerate(self.bfr, start=1):
				rig = self.getObject("Rig", "Split{}".format(i))

				name = self.getObjectName(i, "Jnt")

				mm = self._createNode("multMatrix", "MulMatrix{}".format(i))
				dm = self._createNode("decomposeMatrix", "DecomposeMatrix{}".format(i))

				cmds.connectAttr(bfr+".worldMatrix[0]", mm+".matrixIn[0]")
				cmds.connectAttr(rig+".parentInverseMatrix[0]", mm+".matrixIn[1]")
				cmds.connectAttr(mm+".matrixSum", dm+".inputMatrix")
				cmds.connectAttr(dm+".outputRotate", rig+".rotate")

							
		if self.settings("dynamic"):
			for i, harmonic in enumerate(self.jntparent):
				nodeName = self.getObjectName("Nde", "Harmonic{}".format(i))
				parent = cmds.listRelatives(harmonic, parent=True)[0]
				cns = compounds.harmonic(nodeName, harmonic, parent, 
					amplitude=1.0, 
					decay=self.settings("decay"), 
					frequency=self.settings("frequency"), 
					termination=self.settings("termination"), 
					amplitudeAxis=(self.settings("amplitudeX"), self.settings("amplitudeY"), self.settings("amplitudeZ")))

				if i%3 == 0:
					mulNode = self._createNode("multiplyDivide", name="AmplitudeGlobal{}".format(i))
					activeNode = self._createNode("multiplyDivide", name="Active{}".format(i))
					cmds.connectAttr(mulNode+".output", activeNode+".input1")

					# Connect to Attributes
					mulNode = self.getObjectName("Nde", "AmplitudeGlobal{}".format(i))
					cmds.connectAttr(self.globalAmplAttr, mulNode+".input1X")
					cmds.connectAttr(self.globalAmplAttr, mulNode+".input1Y")
					cmds.connectAttr(self.globalAmplAttr, mulNode+".input1Z")

					activeNode = self.getObjectName("Nde", "Active{}".format(i))
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2X")
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2Y")
					cmds.connectAttr(self.dynamicAttr, activeNode+".input2Z")

				# Connect to Attributes
				axis = "XYZ"[i%3]
				cmds.connectAttr(self.localAmplAttr[i], mulNode+".input2"+axis)
				cmds.connectAttr(activeNode+".output"+axis, cns+".amplitude")

			if self.settings("dynamicAnimatable"):
				cmds.connectAttr(self.axisAttr, cns+".axisAmp")
				cmds.connectAttr(self.decayAttr, cns+".decay")
				cmds.connectAttr(self.terminationAttr, cns+".termination")
				cmds.connectAttr(self.frequencyAttr, cns+".frequencyMult")

	def createConnections(self):

		for port, cnx in self.connections(includeUIHosts=False).iteritems():
			bfr = self.getObject("Bfr", port)
			cnx.connect(bfr)