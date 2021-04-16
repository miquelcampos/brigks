from itertools import izip
from collections import defaultdict

from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, compounds, umath

class ArmSystemBuilder(SystemBuilder):

	twp = ["Upr", "Lwr"]

	def createObjects(self):
		# SIZE
		size = self.translations("Root").distance(self.translations("Elbow"))
		fkSize = size * .5
		ikSize = size * .5
		upvSize = size * .125
		rootSize = size * .25

		# TRANSFORMATIONS
		positions = Vector3Array([self.translations("Root"), self.translations("Elbow"), self.translations("Wrist")])
		normal = Vector3.planeNormal(*positions)
		oriNormal = normal.copy()
		if self.negate():
			normal *= -1
		
		# distances
		d = [(positions[i],positions[i+1]) for i in range(2)]
		self.lengths = [Vector3.distance(a,b) for a,b in d]
		self.lengths.append(1)
		ratio = self.lengths[0] / sum(self.lengths[:2])
		self.setSettings(lengths=self.lengths[:2])
		
		# root
		rootTfm = Transformation.fromParts(translation=self.translations("Root"))

		# fk
		fkTfm = TransformationArray.chain(positions, normal, axis="xz", negativeSide=self.negate(), endTransform=False)
		direction = self.translations("Eff") - self.translations("Wrist")
		fk2Tfm = Transformation.lookAt(self.translations("Wrist"), direction, self.directions("Wrist", "z"), axis="xz", negativeSide=self.negate())
		fkTfm = fkTfm.appended(fk2Tfm)

		bfrTfm = [Transformation.fromParts(translation=tfm.translation, rotation=fkTfm[max(i-1,0)].rotation) for i, tfm in enumerate(fkTfm)]
		bfrTfm[0] = Transformation.lookAt(self.translations("Root"), constants.x_axis, constants.y_axis, axis=self.sign()+"xz", negativeSide=self.negate())
		
		# ik
		ikbfrPos = Vector3([self.factor() * sum(self.lengths[:2]), 0, 0]) * rootTfm.asMatrix()
		ikbfrTfm = Transformation.fromParts(translation=ikbfrPos)
		ikTfm = Transformation.lookAt(self.translations("Wrist"), direction, self.directions("Wrist", "z"), axis=self.sign()+"xy", negativeSide=False)
		
		upvbfrTfm = Transformation.fromParts(translation=umath.upVector(self.translations("Root"), ikbfrPos, constants.y_axis, ratio, self.negate()))
		upvTfm = Transformation.fromParts(translation=umath.upVector(self.translations("Root"), self.translations("Wrist"), oriNormal, ratio))
		
		# extras
		scale = Vector3([self.factor(), self.factor(), self.factor()])
		twisterTfm = {}
		interTfm = {}
		for i, (p, pos) in enumerate(izip(self.twp, positions[1:3])):
			twisterTfm[p] = [fkTfm[i].copy(scale=scale), fkTfm[i].copy(translation=pos, scale=scale)]
			interPos = twisterTfm[p][0].translation.lerp(twisterTfm[p][1].translation, .5)
			interTfm[p] = twisterTfm[p][0].copy(translation=interPos)
			
		ctrTfm = twisterTfm["Lwr"][0]

		# prop
		propTfm = Transformation.lookAt(self.translations("Prop"), self.directions("Prop", "y"), self.directions("Prop", "z"), axis="yz", negativeSide=False)


		# CONTROLLERS
		# Root 
		self.rootBfr = self.createBuffer(None, "Root", rootTfm)
		self.rootCtl = self.createController(self.rootBfr, "Root", rootTfm, "sphere", size=rootSize, color=self.colorIk())
		# self.addToSubControllers(self.rootCtl)
		attributes.setKeyables(self.rootCtl, constants.t_attrs)
		
		# Fk Ref
		# Used as a reference for the upr start twist
		# We cannot use the fk1Bfr cause this one get constrained when fk ref changes
		self.fkRef = self.createRig(self.rootBfr, "FkRef", bfrTfm[0])

		# GinmbalController
		if self.settings("gimbalControllers"):
			fkBfr = self.createBuffer(self.fkRef, "FkOff", tfm=bfrTfm[0])
			self.fkOffCtl = self.createController(fkBfr, "FkOff", bfrTfm[0], "cube", size=.9, so=[0,1,1], color=self.colorFk())
			self.addToSubControllers(self.fkOffCtl)
			fkParent = self.fkOffCtl
			boneParent = self.fkOffCtl
		else:
			fkParent = self.fkRef
			boneParent = self.fkRef

		# FK Controlers and Bones
		self.fkBfr = []
		self.fkCtl = []
		self.bones = []
		self.stretches = []
		for i, (tfm, btfm) in enumerate(izip(fkTfm, bfrTfm), start=1):
			bfr = self.createBuffer(fkParent, "Fk{}".format(i), btfm)
			ctl = self.createController(bfr, "Fk{}".format(i), tfm, "sphere", size=fkSize, so=(0,1,1), color=self.colorFk())

			if self.settings("lockElbowRotation") and i == 2:
				attributes.setRotOrder(ctl, "xyz")
				attributes.setKeyables(ctl, ["tx", "ty", "tz", "rz", "sx", "sy", "sz"], lock=True)
			else:
				attributes.setRotOrder(ctl, "xzy")
				attributes.setKeyables(ctl, constants.trs_attrs)
			
			fkParent = ctl
			self.fkBfr.append(bfr)
			self.fkCtl.append(ctl)

			bone = self.createRig(boneParent, "Bone{}".format(i), tfm=tfm, icon="bone", so=(self.factor(), 1, 1))
			boneParent = bone
			self.bones.append(bone)
			
		# IK Controllers
		self.ikBfr = self.createBuffer(None, "Ik", ikbfrTfm)
		self.ikCtl = self.createController(self.ikBfr, "Ik", ikTfm, "cube", size=ikSize, color=self.colorIk())

		attributes.setKeyables(self.ikCtl, constants.trs_attrs)
		attributes.setRotOrder(self.ikCtl, "XZY")

		self.ikoffCtl = self.createController(self.ikCtl, "IkOffset", ikTfm, "null", size=ikSize, color=self.colorIk())
		# self.addToSubControllers(self.ikoffCtl)
		attributes.setKeyables(self.ikoffCtl, constants.trs_attrs)
		self.ikRef = self.createRig(self.ikoffCtl, "IkRef", fkTfm[-1])
		attributes.setRotOrder(self.ikoffCtl, "XZY")

		self.upvBfr = self.createBuffer(None, "Upv", upvbfrTfm)
		self.upvCtl = self.createController(self.upvBfr, "Upv", upvTfm, "diamond", size=upvSize, color=self.colorIk())
		attributes.setKeyables(self.upvCtl, constants.t_attrs)

		self.ctrBfr = self.createBuffer(self.bones[0], "Center", ctrTfm)
		self.ctrCtl = self.createController(self.ctrBfr, "Center", ctrTfm, "sphere", size=upvSize, color=self.colorIk())
		# self.addToSubControllers(self.ctrCtl)
		attributes.setKeyables(self.ctrCtl, constants.trs_attrs)

		self.upvCrv = create.cnsCurve(self.getObjectName("Rig", "UpvCrv"), [self.upvCtl, self.ctrCtl])
	
		# Twisters
		self.twisters = defaultdict(list)
		for p in self.twp:
			for s, tfm, factor in izip(["Start", "End"], twisterTfm[p], [1,-1]):
				twisterBfr = self.createBuffer(self.rootBfr, "Tw"+p+s, tfm )
				twister = self.createRig(twisterBfr, "Tw"+p+s, tfm, "pyramid")
				self.twisters[p].append(twister)

		# Inter
		self.inters = {}
		for p in self.twp:
			self.inters[p] = self.createRig(self.rootBfr, "Inter"+p, interTfm[p], "cube")

		# Prop Controller
		propBfr = self.createBuffer(self.bones[-1], "Prop", propTfm)
		self.propCtl = self.createController(propBfr, "Prop", propTfm, "cube", color=self.colorIk())

	def createJoints(self):
		for p in self.twp:
			for s, twister in izip(["Start", "End"], self.twisters[p]):
				self.createJoint(twister,  "Tw"+p+s)
		
		self.createJoint(self.ctrCtl, "Center")
		self.createJoint(self.bones[2], "Hand")
	
	#-----------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.blendAttr = self.createAnimAttr("Blend", "float", self.settings("blend") == "IK", 0, 1)

		self.showCtrlAttr = self.createAnimAttr("showCtrl", "bool", False) 

		self.rollAttr = self.createAnimAttr("Roll", "float", 0, -180, 180)
		self.scaleAAttr = self.createAnimAttr("ScaleA", "float", 1)
		self.scaleBAttr = self.createAnimAttr("ScaleB", "float", 1)
		self.maxStretchAttr = self.createAnimAttr("MaxStretch", "float", self.settings("stretchDefault"), 1, None)
		self.slideAttr = self.createAnimAttr("Slide", "float", .5, 0, 1)
		self.reverseAttr = self.createAnimAttr("Reverse", "float", self.settings("reverseDefault"), 0, 1)
		self.softnessAttr = self.createAnimAttr("Softness", "float", 0, 0, 1)

		self.lengthAAttr = self.createSetupAttr("LengthA", "float", self.lengths[0])
		self.lengthBAttr = self.createSetupAttr("LengthB", "float", self.lengths[1])

	def createLayout(self): 
		pass
		
		
	#-----------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibility
		fkCompare = compounds.compare(self.blendAttr, 1, "<")
		ikCompare = compounds.compare(self.blendAttr, 0, ">")

		cmds.connectAttr(self.showCtrlAttr, fkCompare+".colorIfFalseR")
		cmds.connectAttr(self.showCtrlAttr, ikCompare+".colorIfFalseR")

		for ctl in self.fkCtl:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")

		if self.settings("gimbalControllers"):
			for shp in cmds.listRelatives(self.fkOffCtl, shapes=True):
				cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")

		for ctl in [self.rootCtl, self.ikCtl, self.ikoffCtl, self.upvCtl, self.upvCrv]:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(ikCompare+".outColorR", shp+".visibility")

		# Center
		attributes.inheritsTransform(self.ctrBfr, False)
		node = self._createNode("decomposeMatrix", "CtrDM")
		cmds.connectAttr(self.bones[1]+".worldMatrix[0]", node+".inputMatrix")
		cmds.connectAttr(node+".outputTranslate", self.ctrBfr+".translate")
		cns = compounds.blendMatrix(self.ctrBfr, self.bones[:2], maintainOffset=False, translate=False, rotate=True, scale=False)
		cmds.setAttr(cns+".target[1].weight", .5)
		for s in 'XYZ':
			cmds.connectAttr(self.nodes("local")+".sx", self.ctrBfr+".scale{}".format(s))
		
		# Fk Ik Solver
		iks = [self.rootCtl, self.ikRef, self.upvCtl]
		ikfkNode = compounds.fkik2Bones(iks, self.fkCtl, self.bones, self.lengths[0], self.lengths[1], self.negate())
		cmds.connectAttr(self.blendAttr, ikfkNode+".blend")
		cmds.connectAttr(self.rollAttr, ikfkNode+".roll")
		cmds.connectAttr(self.scaleAAttr, ikfkNode+".scaleA")
		cmds.connectAttr(self.scaleBAttr, ikfkNode+".scaleB")
		cmds.connectAttr(self.maxStretchAttr, ikfkNode+".maxStretch")
		cmds.connectAttr(self.slideAttr, ikfkNode+".slide")
		cmds.connectAttr(self.reverseAttr, ikfkNode+".reverse")
		cmds.connectAttr(self.softnessAttr, ikfkNode+".softness")
		cmds.connectAttr(self.lengthAAttr, ikfkNode+".lengthA")
		cmds.connectAttr(self.lengthBAttr, ikfkNode+".lengthB") 

		# # Twisters
		self._twisterCns(self.twisters["Upr"][0], self.bones[0], self.ctrCtl, self.fkRef, self.bones[0], self.sign()+"xz", self.lengths[0])
		self._twisterCns(self.twisters["Upr"][1], self.ctrCtl, self.bones[0], self.ctrCtl, self.ctrBfr, self.nsign()+"xz", self.lengths[0], scaleComp=True)
		self._twisterCns(self.twisters["Lwr"][0], self.ctrCtl, self.bones[-1], self.ctrCtl, self.ctrBfr, self.sign()+"xz", self.lengths[1], scaleComp=True)
		self._twisterCns(self.twisters["Lwr"][1], self.bones[-1], self.ctrCtl, self.bones[2], self.bones[1], self.nsign()+"xy", self.lengths[1], pntAtDouble=False)
		
		# # Inter
		for p in self.twp:
			cmds.pointConstraint(self.twisters[p], self.inters[p])
			cns = compounds.aimConstraint(self.getObjectName("Nde", "Aim"), self.inters[p], self.twisters[p][1], axis="x-z")
			compounds.spinePointAt(cns, self.twisters[p][0], self.twisters[p][1], blend=.5, solver=1) 
		
	
	def _twisterCns(self, tws, pos, aim, pntAt, pntAtRef, axis, distance, pntAtDouble=True, scaleComp=False):
		attributes.inheritsTransform(tws, False)

		# Position
		node = self._createNode("decomposeMatrix", "TwsDM")
		cmds.connectAttr(pos+".worldMatrix[0]", node+".inputMatrix")
		cmds.connectAttr(node+".outputTranslate", tws+".translate")

		# Rotation 
		if pntAtDouble:
			cns = compounds.aimConstraint(self.getObjectName("Nde", "Aim"), tws, aim, axis=axis, upMaster=None, upVector=(0,0,1))
			compounds.pointAtDoubleAxis(cns, pntAtRef, pntAt, axis="z")
		else:
			cns = compounds.aimConstraint(self.getObjectName("Nde", "Aim"), tws, aim, axis=axis, upMaster=pntAt, upVector=(0,1,0))
			
		# Scaling
		dist_Node = self._createNode("distanceBetween", "twsScaleDist")
		cmds.connectAttr(pos+".worldMatrix[0]", dist_Node+".inMatrix1")
		cmds.connectAttr(aim+".worldMatrix[0]", dist_Node+".inMatrix2")
		div_Node = self._createNode("multiplyDivide", "twsScaleRatio")
		cmds.setAttr(div_Node+".operation", 2) # Division
		cmds.connectAttr(dist_Node+".distance", div_Node+".input1X")
		cmds.setAttr(div_Node+".input2X", distance)
		cmds.connectAttr(div_Node+".outputX", tws+".scaleX")

		if scaleComp:
			divNode = self._createNode("multiplyDivide", "Div")
			cmds.setAttr(divNode+".operation", 1)  # Multiply
			cmds.connectAttr(pos+".scale", divNode+".input1")
			cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2X")
			cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2Y")
			cmds.connectAttr(self.nodes("local")+".sx", divNode+".input2Z")

			cmds.connectAttr(divNode+".outputY", tws+".scaleY")
			cmds.connectAttr(divNode+".outputZ", tws+".scaleZ")
		else:
			cmds.connectAttr(pos+".sy", tws+".scaleY")
			cmds.connectAttr(pos+".sz", tws+".scaleZ")


	#-----------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		# Root
		rootBfr = self.getObject("Root", "Hbfr")
		self.connect_parenting(rootBfr, "Root")
		
		# Ik Ref
		ikBfr = self.getObject("Ik", "Hbfr")
		upvBfr = self.getObject("Upv", "Hbfr")
		self.connect_parenting(ikBfr, "IkRef", paramName="IkRef")
		self.connect_parenting(upvBfr, "IkRef", paramName="UpvRef")
		
		# Fk Ref
		if self.settings("gimbalControllers"):
			fk1Bfr = self.getObject("FkOff", "Hbfr")
		else:
			fk1Bfr = self.getObject("Fk1", "Hbfr")
		self.connect_orientation(fk1Bfr, "FkRef", paramName="FkRef")