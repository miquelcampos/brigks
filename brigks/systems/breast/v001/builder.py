from itertools import izip

from maya import cmds

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, compounds, umath

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array


class BreastSystemBuilder(SystemBuilder):

	
	def createObjects(self):
		# SIZE
		size = self.translations("Root").distance(self.translations("Eff"))

		# TRANSFORMATION
		# Normal
		normal = self.directions("Root", "z")
		
		direction = self.translations("Eff") - self.translations("Root") 
		rootTfm = Transformation.lookAt(self.translations("Root"), direction, normal, self.nsign()+"yz", self.negate())
		dynTfm = Transformation.lookAt(self.translations("Root"), direction, normal, "xz", self.negate())
		posTfm = dynTfm.copy(translation=self.translations("Eff"))
		
		upvPos = Vector3([0,0,10]) * dynTfm.asMatrix()

		# OBJECTS
		# Controller
		self.dynBfr = self.createBuffer(None, "1", dynTfm)
		self.dynCtl = self.createController(self.dynBfr, "1", dynTfm, "sphere", size=size, po=(self.factor(),0,0), so=(1,1,0), color=self.colorFk())
		attributes.setKeyables(self.dynCtl)
		# self.setInversedParameters(self.dynCtl, middle=["posz", "rotx", "roty"])
		
		self.posBfr = self.createBuffer(self.dynBfr, "2", posTfm)
		self.posCtl = self.createController(self.posBfr, "2", posTfm, "sphere", size=size*1.5, so=[0,1,1], color=self.colorIk())
		attributes.setKeyables(self.posCtl)
		# self.setInversedParameters(self.posCtl, middle=["posz", "rotx", "roty"])

		# Dynamic ----------------------------
		self.harmonic = self.createRig(self.posCtl, "Harmonic", posTfm, "diamond", size=1)

			
	def createJoints(self):
		self.createJoint(self.harmonic, "1")
			
	#-------------------------------------------------------------------------------
	# PROPERTIES 
	def createAttributes(self):
		self.dynamicAttr = self.createAnimAttr("dynamic", "bool", self.settings("dynActive"))
		self.amplitudeAttr = self.createAnimAttr("amplitude", "float", self.settings("amplitude"), 0, 5)
		
		if self.settings("dynamicAnimatable"):
			self.axisAttr = self.createAnimAttr("axis", "vector", (self.settings("amplitudeX"), self.settings("amplitudeY"), self.settings("amplitudeZ")))
			self.decayAttr = self.createAnimAttr("decay", "float", self.settings("decay"), 0, 10)
			self.terminationAttr = self.createAnimAttr("termination", "float", self.settings("termination"), 0, 1)
			self.frequencyAttr = self.createAnimAttr("frequency", "float", self.settings("frequency"), 0, 1)
		
	#-------------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		cns = compounds.harmonic(self.getObjectName("Nde", "Harmonic"), self.harmonic, self.posCtl, 
			amplitude=1.0, 
			decay=self.settings("decay"), 
			frequency=self.settings("frequency"), 
			termination=self.settings("termination"), 
			amplitudeAxis=(self.settings("amplitudeX"), self.settings("amplitudeY"), self.settings("amplitudeZ")))

		activeNode = self._createNode("multiplyDivide", name="active")
		cmds.connectAttr(self.amplitudeAttr, activeNode+".input1X")
		cmds.connectAttr(self.dynamicAttr, activeNode+".input2X")

		cmds.connectAttr(activeNode+".outputX", cns+".amplitude")

		if self.settings("dynamicAnimatable"):
			cmds.connectAttr(self.axisAttr, cns+".axisAmp")
			cmds.connectAttr(self.decayAttr, cns+".decay")
			cmds.connectAttr(self.terminationAttr, cns+".termination")
			cmds.connectAttr(self.frequencyAttr, cns+".frequencyMult")
		
		# Vertical controller
		compounds.blendMatrix(self.posBfr, [self.dynCtl], maintainOffset=True, rotate=False, scale=False)
					

	#-------------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		root = self.getObject("1", usage="Hbfr")
		self.connect_parenting(root, "Root")
