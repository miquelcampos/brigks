from itertools import izip

from maya import cmds

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, compounds, umath

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

class DrivenSystemBuilder(SystemBuilder):

	def createObjects(self):
		# TRANSFORMATION
		rootTfm = self.transforms("Rail")
		posTfm = self.transforms("Pos")
		negTfm = self.transforms("Neg")

		for i, (root,pos,neg) in enumerate(izip(rootTfm,posTfm,negTfm), start=1):
			root.scale = self.scales("Rail{}".format(i))
			pos.scale = self.scales("Pos{}".format(i))
			neg.scale = self.scales("Neg{}".format(i))
		
		# CONTROLLERS
		self._rails = []
		self._psts = []
		self._ngts = []
		self._slds = []
		self._bfrs = []
		for i, (rtfm, ptfm, ntfm) in enumerate(izip(rootTfm, posTfm, negTfm), start=1):
			rail = self.createRig(None, "Rail{}".format(i), rtfm, "cube", size=1)
			pos = self.createRig(rail, "Pos{}".format(i), ptfm, "null", size=1)
			neg = self.createRig(rail, "Neg{}".format(i), ntfm, "cube", size=1)

			bfr = self.createBuffer(rail, "Slider{}".format(i), rtfm)
			if self.settings("addControllers"):
				slider = self.createController(bfr, "Part{}".format(i), rtfm, "sphere", color=self.colorIk())
				attributes.setKeyables(slider)
			else:
				slider = self.createRig(bfr, "Part{}".format(i), rtfm, "sphere", size=1)

			create.cnsCurve("Crv{}".format(i), [neg,rail,pos], degree=1)

			self._bfrs.append(bfr)
			self._rails.append(rail)
			self._slds.append(slider)
			self._psts.append(pos)
			self._ngts.append(neg)
		

	def createJoints(self):
		for i, (slider,rail) in enumerate(izip(self._slds, self._rails), start=1):
			if self.settings("addDeformerRef"):
				ref = rail
			else:
				ref = None
			self.createJoint(slider, str(i), reference=ref)

	#----------------------------------------------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.outrotAttr = self.createSetupAttr("OutRot", "float3", (0,0,0))
		self.slideAttr = [self.createSetupAttr("Slide{}".format(i), "float", 0, -1.0, 1.0) for i in xrange(1, self.count("Rail")+1)]


	#----------------------------------------------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		axis = ["XYZ".index(self.settings("axis{}".format(i))) for i in xrange(1, self.count("Rail")+1)]
		rots = [(self.settings("minRot{}".format(i)), self.settings("maxRot{}".format(i))) for i in xrange(1, self.count("Rail")+1)]

		for rail, pos, neg, slider, rot, a, slide in izip(self._rails, self._psts, self._ngts, self._bfrs, rots, axis, self.slideAttr):
			# Slider Op
			cns = compounds.rotationToSlider(slide, rotMin=rot[0], rotMax=rot[1], slideMin=-1, slideMax=1)
			cmds.connectAttr(self.outrotAttr+str(a), cns+".angle")

			# Blending Constraints
			bmNode = compounds.blendMatrix(slider, [rail, pos, neg])

			# Positive Expression
			# Returns Maximum Value (There's no min/max node in Maya)
			condPosNode = self._createNode("condition", name="condPos")
			cmds.setAttr(condPosNode+".operation", 2)# Greater Than >
			cmds.connectAttr(slide, condPosNode+".firstTerm")
			cmds.connectAttr(slide, condPosNode+".colorIfTrueR")
			cmds.setAttr(condPosNode+".secondTerm", 0)
			cmds.setAttr(condPosNode+".colorIfFalseR", 0)

			# Negative Expression
			# Returns Negative Value (There's no neg node in Maya)
			negNode = self._createNode("multiplyDivide", name="neg")
			cmds.connectAttr(slide, negNode+".input1X")
			cmds.setAttr(negNode+".input2X", -1)

			# Returns Maximum Value (There's no min/max node in Maya)
			condNegNode = self._createNode("condition", name="condNeg")
			cmds.setAttr(condNegNode+".operation", 2)# Greater Than >
			cmds.connectAttr(negNode+".outputX", condNegNode+".firstTerm")
			cmds.connectAttr(negNode+".outputX", condNegNode+".colorIfTrueR")
			cmds.setAttr(condNegNode+".secondTerm", 0)
			cmds.setAttr(condNegNode+".colorIfFalseR", 0)

			cmds.connectAttr(condPosNode+".outColorR", bmNode+".target[1].weight")
			cmds.connectAttr(condNegNode+".outColorR", bmNode+".target[2].weight")

	#----------------------------------------------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		rails = [self.getObject("Rail{}".format(i), usage="Rig") for i in xrange(1, self.count("Rail")+1)]
		
		if self.settings("connectionType") == "standard":
			self.connect_hierarchyParenting(rails, "Rail")
		elif self.settings("connectionType") == "obj2cls":
			self.connect_hierarchyObject2Cluster(rails, "RailCls")
		elif self.settings("connectionType") == "customParent":
			self.connect_hierarchyCustomParenting(rails, "RailCustom")
		
		
		reference = self.connectionObject("Reference")
		tracker = self.connectionObject("Tracker")
		outrotAttr = self.attributes("OutRot", "setup")
		
		if None in [reference, tracker]:
			return

		cns = self._createCompound("rotationTrackerNode", outrotAttr.nativePointer(), reference, tracker)
			