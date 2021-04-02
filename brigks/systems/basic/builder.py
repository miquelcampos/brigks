from maya import cmds

from brigks.core.useful import trs_attrs, setRotOrder, setKeyables, createHarmonic
from brigks.systems.systemBuilder import SystemBuilder

class BasicSystemBuilder(SystemBuilder):

	def createObjects(self):
		self.bfr = []
		self.ctl = []
		parent = None

		color = self.settings["colorIk"] if self.settings["useIkColor"] else self.settings["colorFk"]
		axis = self.sign()+"yz"

		self.jntHost = []
		for i, (part, marker) in enumerate(self.guide.markers.iteritems()):
			bfr = self.createBuffer(None, part, tfm=marker.transform())
			self.bfr.append(bfr)

			if self.settings["addControllers"]:
				ctl = self.createController(bfr, part, tfm=marker.transform(), icon="cube", color=color)
				self.ctl.append(ctl)	
				setRotOrder(ctl, self.settings["defaultRotationOrder"])

				keyables = [attr for attr in trs_attrs if self.settings[attr]]
				setKeyables(ctl, keyables)
				# self.setInversedParameters(ctl, middle=["posx", "rotz", "roty"])
				jntHost = ctl
			else:
				jntHost = bfr

			if self.settings["dynamic"]:
				harmonic = self.createRig(jntHost, "Harmonic%s"%i, tfm=marker.transform())
				jntHost = harmonic

			self.jntHost.append(jntHost)

	def createJoints(self):
		for i, jntHost in enumerate(self.jntHost, start=1):
			self.createJoint(jntHost, i)
			if self.settings["splitRotation"]:
				jnt = self.createJoint(jntHost, "Pos{}".format(i))					
				if self.settings["addControllers"]:
					value = cmds.getAttr(jnt+".radius") *.9
					cmds.setAttr(jnt+".radius", value)

	#----------------------------------------------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		if self.settings["splitRotation"]:
			for i, bfr in enumerate(self.bfr, start=1):
				jnt = self.getObject("Jnt", "Pos{}".format(i))

				name = self.getObjectName(i, "Jnt")

				mm = self._createNode("multMatrix", "MulMatrix{}".format(i))
				dm = self._createNode("decomposeMatrix", "DecomposeMatrix{}".format(i))

				cmds.connectAttr(bfr+".worldMatrix[0]", mm+".matrixIn[0]")
				cmds.connectAttr(jnt+".parentInverseMatrix[0]", mm+".matrixIn[1]")
				cmds.connectAttr(mm+".matrixSum", dm+".inputMatrix")
				cmds.connectAttr(dm+".outputRotate", jnt+".rotate")
							
		if self.settings["dynamic"]:
			for i, harmonic in enumerate(self.jntHost):
				nodeName = self.getObjectName("Nde", "Harmonic{}".format(i))
				parent = cmds.listRelatives(harmonic, parent=True)[0]
				cns = createHarmonic(nodeName, harmonic, parent, 
					amplitude=1.0, 
					decay=self.settings["decay"], 
					frequency=self.settings["frequency"], 
					termination=self.settings["termination"], 
					amplitudeAxis=(self.settings["amplitudeX"], self.settings["amplitudeY"], self.settings["amplitudeZ"]))

				if i%3 == 0:
					mulNode = self._createNode("multiplyDivide", name="AmplitudeGlobal{}".format(i))
					activeNode = self._createNode("multiplyDivide", name="Active{}".format(i))
					cmds.connectAttr(mulNode+".output", activeNode+".input1")

	#----------------------------------------------------------------------------
	# PROPERTIES 
	def createAttributes(self):
		if self.settings["dynamic"]:
			count = len(self.guide.markers)
			dynamicAttr = self.createAnimAttr("Dynamic", "bool", self.settings["dynActive"])
			globalAmplitudeAttr = self.createAnimAttr("GlobalAmplitude", "float", self.settings["amplitude"], 0, 5)
			localAmplitudeAttr = [self.createAnimAttr("LocalAmplitude%s"%i, "float", 1, 0, 10) for i in xrange(count)]

			# Connect
			harmonics = cmds.ls(self.getObjectName("Nde", "Harmonic*"))
			for i, harmonic in enumerate(sorted(harmonics)):
				if i%3 == 0:
					mulNode = self.getObjectName("Nde", "AmplitudeGlobal{}".format(i))
					cmds.connectAttr(globalAmplitudeAttr, mulNode+".input1X", force=True)
					cmds.connectAttr(globalAmplitudeAttr, mulNode+".input1Y", force=True)
					cmds.connectAttr(globalAmplitudeAttr, mulNode+".input1Z", force=True)

					activeNode = self.getObjectName("Nde", "Active{}".format(i))
					cmds.connectAttr(dynamicAttr, activeNode+".input2X", force=True)
					cmds.connectAttr(dynamicAttr, activeNode+".input2Y", force=True)
					cmds.connectAttr(dynamicAttr, activeNode+".input2Z", force=True)

				axis = "XYZ"[i%3]
				cmds.connectAttr(localAmplitudeAttr[i], mulNode+".input2"+axis, force=True)
				cmds.connectAttr(activeNode+".output"+axis, harmonic+".amplitude", force=True)

			if self.settings["dynamicAnimatable"]:
				axisAttr = self.createAnimAttr("Axis", "double3", (self.settings["amplitudeX"], self.settings["amplitudeY"], self.settings["amplitudeZ"]))
				decayAttr = self.createAnimAttr("Decay", "float", self.settings["decay"], 0, 10)
				terminationAttr = self.createAnimAttr("Termination", "float", self.settings["termination"], 0, 1)
				frequencyAttr = self.createAnimAttr("Frequency", "float", self.settings["frequency"], 0, 1)

				# Connect
				cmds.connectAttr(axisAttr, harmonic+".axisAmp", force=True)
				cmds.connectAttr(decayAttr, harmonic+".decay", force=True)
				cmds.connectAttr(terminationAttr, harmonic+".termination", force=True)
				cmds.connectAttr(frequencyAttr, harmonic+".frequencyMult", force=True)

