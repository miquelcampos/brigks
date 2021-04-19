from itertools import izip

from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, compounds, umath
from brigks import config

class NeckSystemBuilder(SystemBuilder):

	def createObjects(self):
		# Settings
		self.isFk = "FK" in self.settings("kinematic")
		self.isIk = "IK" in self.settings("kinematic")
		self.isFkIk = self.isFk and self.isIk
		self.isNotIk = self.isFk and not self.isIk
		self.isNotFk = not self.isFk and self.isIk


		# TRANSFORMATIONS
		positions = Vector3Array([self.translations("Root"), self.translations("Head"), self.translations("Eff")])
		normal = Vector3.planeNormal(*positions)
		if self.negate():
			normal *= -1
		self.neckLength = self.translations("Root").distance(self.translations("Head"))
		headLength = self.translations("Head").distance(self.translations("Eff"))
		
		direction = self.translations("Eff") - self.translations("Head")
		ikTfm = Transformation.lookAt(self.translations("Head"), direction, normal, "yx", self.negate())
		if self.settings("orientToWorld"):
			headTfm = Transformation.fromParts(translation=self.translations("Head"))
		else:
			headTfm = ikTfm
		
		crvPos = Vector3Array([self.translations("Root").lerp(self.translations("Head"), i/3.0) for i in xrange(4)])
		refPos = Vector3Array([self.translations("Root").lerp(self.translations("Head"), i/2.0) for i in xrange(3)])
		direction = self.translations("Head") - self.translations("Root")
		rootTfm = Transformation.lookAt(self.translations("Root"), direction, normal, "yx", self.negate())
		midTfm = rootTfm.copy(translation=refPos[1])
		endTfm = rootTfm.copy(translation=refPos[2])
		tan0Tfm = rootTfm.copy(translation=crvPos[1])
		tan1Tfm = ikTfm.copy(translation=crvPos[-2])
		
		bonePos = refPos.appended(self.translations("Eff"))
		boneTfm = TransformationArray.chain(bonePos, normal, axis="yx", negativeSide=self.negate())


		# CONTROLLERS
		# Root
		self.rootRig = self.addRig(None, "Root", rootTfm)
		self.tan0 = self.addRig(self.rootRig, "Tan0", tan0Tfm)
		
		# Ik 
		self.ikBfr = self.addBfr(self.rootRig, "Ik", headTfm)
		self.ikOri = self.addBfr(self.ikBfr, "IkOri", headTfm) # Maya requires an extra object for the ori cns
		self.ikCtl = self.addCtl(self.ikOri, "Ik", ikTfm, "cube", size=1, 
			po=(0,headLength*.5,0), so=(8, headLength, 8),color=self.colorIk())   
		# self.setInversedsettings(self.ikCtl, middle=["posx", "roty", "rotz"])
		attributes.setRotOrder(self.ikCtl, "XZY")
		self.tan1 = self.addRig(self.ikCtl, "Tan1", tan1Tfm)

		if self.settings("gimbalControllers"):
			self.ikOffCtl = self.addCtl(self.ikCtl, "IkOff", ikTfm, "cube", size=.9, 
				po=(0,headLength*.5,0), so=(8, headLength, 8),color=self.colorIk())   
			# self.setInversedsettings(self.ikOffCtl, middle=["posx", "roty", "rotz"])
			attributes.setKeyables(self.ikOffCtl, constants.r_attrs)
			attributes.setRotOrder(self.ikOffCtl, "XZY")
			self.lastIkCtl = self.ikOffCtl
			# self.addToSubControllers(self.ikOffCtl)
		else:
			self.lastIkCtl = self.ikCtl
		
		# Curve
		self.crv = create.curve("Crv", crvPos, closed=False, degree=3, parent=self.rootRig)

		# References
		self.baseBfr = self.addBfr(self.rootRig, "Base", rootTfm)
		self.baseCtl = self.addCtl(self.baseBfr, "Base", rootTfm, "sphere", size=4, so=(1,0,1), color=self.colorIk())
		# self.setInversedsettings(self.baseCtl, middle=["posx", "roty", "rotz"])
		attributes.setRotOrder(self.baseCtl, "XZY")
		
		self.midBfr = self.addBfr(self.crv, "Mid", midTfm)
		self.midCtl = self.addCtl(self.midBfr, "Mid", midTfm, "sphere", size=4, so=(1,0,1), color=self.colorIk())
		attributes.setKeyables(self.midCtl, constants.ts_attrs)
		# self.setInversedsettings(self.midCtl, middle=["posx"])
		
		self.headBfr = self.addBfr(self.crv, "Head", endTfm)
		if self.settings("extraHeadController"):
			self.headCtl = self.addCtl(self.headBfr, "Head", rootTfm, "sphere", so=(1,0,1), color=self.colorIk())
			# self.addToSubControllers(self.headCtl)
			# self.setInversedsettings(self.headCtl, middle=["posx", "roty", "rotz"])
			attributes.setRotOrder(self.headCtl, "XZY")
			self.headRef = self.headCtl
		else:
			self.headRef = self.headBfr
		
		# Fk
		if self.isFk:
			self.fkCtl = []
			parent = self.rootRig
			for i, tfm in enumerate(boneTfm, start=1):
				if self.settings("orientToWorld") and i == len(boneTfm):
					bfr = self.addBfr(parent, "Fk%s"%i, headTfm)
				else:
					bfr = self.addBfr(parent, "Fk%s"%i, tfm)
				ctl = self.addCtl(bfr, "Fk%s"%i, tfm, "cube", size=8, so=(1,.1,1), color=self.colorFk())
				attributes.setRotOrder(ctl, "XZY")
				
				parent = ctl

				self.fkCtl.append(ctl)

			if self.settings("gimbalControllers"):
				self.fkOffCtl = self.addCtl(self.fkCtl[-1], "fkOffCtl", boneTfm[-1], "cube", size=7.5, so=(1,.1,1), color=self.colorFk())
				attributes.setKeyables(self.fkOffCtl, constants.r_attrs)
				attributes.setRotOrder(self.fkOffCtl, "XZY")

		# Hooks
		self.ikParents = [self.baseCtl, self.midCtl, self.headRef]
		self.hooks = []
		for i, (tfm, parent) in enumerate(izip(boneTfm, self.ikParents), start=1):

			hk = self.addRig(parent, "Hook%s"%i, tfm)
			self.hooks.append(hk)


	def createJoints(self):
		for i, hk in enumerate(self.hooks, start=1):
			if i == 3: i = "Head"
			self.addJnt(hk, i)
	
	#----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		if self.settings("kinematic") == "FK/IK":
			self.blendAttr = self.addAnimAttr("Blend", "float", self.settings("blend")=="IK", 0, 1)
			self.showCtrlAttr = self.addAnimAttr("showCtrl", "bool", False) 

		self.stretchAttr = self.addAnimAttr("Stretch", "float", self.settings("stretch"), 0, 1)
		
		self.lengthAttr = self.addSetupAttr("Length", "float", self.neckLength, 0)
		
		
	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibilities
		fkCompare = compounds.compare(self.blendAttr, 1, "<")
		ikCompare = compounds.compare(self.blendAttr, 0, ">")

		for ctl in self.fkCtl:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")

		for ctl in [self.baseCtl, self.midCtl, self.ikCtl]:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(ikCompare+".outColorR", shp+".visibility")

		if self.settings("gimbalControllers"):
			for shp in cmds.listRelatives(self.fkOffCtl, shapes=True):
				cmds.connectAttr(fkCompare+".outColorR", shp+".visibility")
			for shp in cmds.listRelatives(self.ikOffCtl, shapes=True):
				cmds.connectAttr(ikCompare+".outColorR", shp+".visibility")

		# Cluster Centers
		compounds.curvePointCenters(self.crv, self.rootRig, 0)
		compounds.curvePointCenters(self.crv, self.tan0, 1)
		compounds.curvePointCenters(self.crv, self.tan1, 2)
		compounds.curvePointCenters(self.crv, self.lastIkCtl, 3)

		# Direction
		cns = compounds.aimConstraint(self.getObjectName(config.USE_NDE, "Aim"), self.baseBfr, self.midCtl, 
								axis=self.sign()+"yx", upMaster=self.rootRig, upVector=(1,0,0))

		# Stretch
		outStretch = self._createStretchOperator()
		
		# Curve Cns
		crvCns = compounds.curveConstraints(self.midBfr, self.crv, axis=self.sign()+"y-z", parametric=False, u=.5)
		condANode = self._createNode("condition", name="Condition")
		cmds.connectAttr(outStretch, condANode+".colorIfTrueR")
		cmds.setAttr(condANode+".colorIfFalseR", 1)
		mulNode = self._createNode("multiplyDivide", name="050Perc")
		cmds.connectAttr(condANode+".outColorR", mulNode+".input1X")
		cmds.setAttr(mulNode+".input2X", .5)
		cmds.connectAttr(mulNode+".outputX", crvCns+".uValue")
		compounds.spinePointAt(crvCns, self.rootRig, self.lastIkCtl, blend=.5, solver=1) 
		crvCns = compounds.curveConstraints(self.headBfr, self.crv, axis=self.sign()+"y-z", parametric=False, u=1)
		cmds.connectAttr(outStretch, crvCns+".uValue")

		cmds.parentConstraint([self.lastIkCtl], self.headBfr, maintainOffset=True, name=self.getObjectName(config.USE_NDE, "Orient"))
		cmds.connectAttr(self.nodes("local")+".scale", self.headBfr+".scale")
		cmds.connectAttr(self.nodes("local")+".scale", self.midBfr+".scale")

		# Hooks
		if self.isFkIk:
			if self.settings("gimbalControllers"):
				fkCtl = self.fkCtl[:-1] + [self.fkOffCtl]
			else:
				fkCtl = self.fkCtl

			for ikm, fkm, hook, in izip(self.ikParents, fkCtl, self.hooks):
				cns = compounds.blendMatrix(hook, [ikm, fkm], maintainOffset=True)
				cmds.connectAttr(self.blendAttr, cns+".target[1].weight")

	def _createStretchOperator(self):
		ciNode = self._createNode("curveInfo", "CurveInfo")
		shape = cmds.listRelatives(self.crv, shapes=True)[0]
		cmds.connectAttr(shape+".worldSpace[0]", ciNode+".inputCurve")

		scaleNode = self._createNode("multiplyDivide", "LengthRescale")
		cmds.setAttr(scaleNode+".operation", 2) # Division
		cmds.connectAttr(ciNode+".arcLength", scaleNode+".input1X")
		cmds.connectAttr(self.nodes("local")+".sx", scaleNode+".input2X")

		divNode = self._createNode("multiplyDivide", "DivLengthRatio")
		cmds.setAttr(divNode+".operation", 2) # Division
		cmds.setAttr(divNode+".input1X", self.neckLength)
		cmds.connectAttr(scaleNode+".outputX", divNode+".input2X")

		negNode = self._createNode("multiplyDivide", "Neg")
		cmds.connectAttr(self.stretchAttr, negNode+".input1X")
		cmds.setAttr(negNode+".input2X", -1)

		addNodeA = self._createNode("addDoubleLinear", "AddA")
		cmds.setAttr(addNodeA+".input1", 1)
		cmds.connectAttr(negNode+".outputX", addNodeA+".input2")

		mulNode = self._createNode("multiplyDivide", "Mul")
		cmds.connectAttr(divNode+".outputX", mulNode+".input1X")
		cmds.connectAttr(addNodeA+".output", mulNode+".input2X")

		addNodeB = self._createNode("addDoubleLinear", "AddB")
		cmds.connectAttr(mulNode+".outputX", addNodeB+".input1")
		cmds.connectAttr(self.stretchAttr, addNodeB+".input2")

		return addNodeB+".output"


	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		if "Root" in self.connections():
			root = self.getObject(config.USE_RIG, "Root")
			self.connections("Root").connect(root)

		if "IK" in self.connections():
			root = self.getObject(config.USE_BFR, "Ik")
			self.connections("IK").connect(root, attrName="IkParent")

		if "Orient" in self.connections():
			root = self.getObject(config.USE_BFR, "IkOri")
			self.connections("Orient").connect(root, attrName="IkOrient")
			root = self.getObject(config.USE_BFR, "Fk3")
			self.connections("Orient").connect(root, attrName="FkOrient")
