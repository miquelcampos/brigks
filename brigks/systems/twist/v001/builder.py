from maya import cmds

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, compounds, umath

class TwistSystemBuilder(SystemBuilder):

	def createObjects(self):

		self.axis = self.settings("axis").lower()

		# TRANSFORMATIONS
		positions = self.translations("Part")

		# Normal
		if self.count("Part") > 2:
			normal = Vector3.planeNormal(*positions[:3])
			if normal.length() < 1E-6:
				normal = self.directions("Part1", "z")
		else:
			normal = self.directions("Part1", "z")

		ctlTfm = TransformationArray.chain(positions, normal, axis=self.axis+"z", negativeSide=self.negate(), endTransform=True)

		divTfm = Transformation()
		if self.negate():
			divTfm.scaling = Vector3([-1,-1,-1])

		length = self.translations("Part1").distance(self.translations("Part2")) / 5.0


		# CONTROLLERS
		self._centers = []

		# Left this dictionary in here, just in case we wanna revert back
		shdScl = [length,length,length]
		shdScl["xyz".index(self.axis)] = 0

		se_keyableParameters = list(constants.tr_attrs)
		int_keyableParameters = list(constants.t_attrs)

		if self.settings("scaleWithControllers"):
			se_keyableParameters += ["scl"+s for s in "xyz" if s != self.axis]

		if self.settings("scaleWithInterControllers"):
			int_keyableParameters += ["scl"+s for s in "xyz" if s != self.axis]

		# Start Controller
		bfr = self.createBuffer(None, "Start", ctlTfm[0])
		if self.settings("startController"):
			ctl = self.createController(bfr, "Start", ctlTfm[0], "sphere", so=shdScl, color=self.colorFk())
			attributes.setKeyables(ctl, se_keyableParameters)
			self._centers.append(ctl)
		else:
			self._centers.append(bfr)

		# Inter Controller
		for i, tfm in enumerate(ctlTfm[1:-1], start=1):

			bfr = self.createBuffer(None, "Part%s"%i, tfm)

			if self.settings("interControllers"):
				ctl = self.createController(bfr, "Part%s"%i, tfm, "cube", size=2, so=shdScl, color=self.colorFk())
				attributes.setKeyables(ctl, int_keyableParameters)
				self._centers.append(ctl)
			else:
				self._centers.append(bfr)

		# End Controller
		bfr = self.createBuffer(None, "End", ctlTfm[-1])
		if self.settings("endController"):
			ctl = self.createController(bfr, "End", ctlTfm[-1], "sphere", so=shdScl, color=self.colorFk())
			attributes.setKeyables(ctl, se_keyableParameters)
			self._centers.append(ctl)
		else:
			self._centers.append(bfr)


		# CURVE
		# tangent = self.settings("tangentDistance") if self.settings("tangent") else None
		self.crv = create.cnsCurve("curve", self._centers, closed=False, degree=3)
		self.length = cmds.arclen(self.crv)

		# DIVISIONS
		parent = self._centers[0]
		self.start_iter = 0 if self.settings("startDeformer") and not self.settings("tangent") else 1
		if self.settings("tangent"):
			self.interDiv = [self.createRig(parent, "Div%s"%i, divTfm, "cube", size=2) for i in xrange(1, self.settings("interDeformers")+1)]
			if self.settings("untwistDeformers"):
				self.unTwistDiv = [self.createRig(parent, "Untwist%s"%i, divTfm, "cube", size=1) for i in xrange(1, self.settings("interDeformers")+1)]
				self.unTwistStart = self.createRig(self._centers[0], "UntwistStart", ctlTfm[0], "cube", size=1)
				self.unTwistEnd = self.createRig(self._centers[-1], "UntwistEnd", ctlTfm[-1], "cube", size=1)
		else:
			div_count = self.settings("interDeformers") + self.settings("startDeformer") + self.settings("endDeformer")
			self.interDiv = [self.createRig(parent, "Div%s"%i, divTfm, "cube", size=2) for i in xrange(self.start_iter, div_count+self.start_iter)]
			if self.settings("untwistDeformers"):
				self.unTwistDiv = [self.createRig(parent, "Untwist%s"%i, divTfm, "cube", size=1) for i in xrange(self.start_iter, div_count+self.start_iter)]

	def createJoints(self):
		if self.settings("tangent"):
			if self.settings("startDeformer"):
				self.createJoint(self._centers[0], "0")

			for i, interDiv in enumerate(self.interDiv, start=1):
				self.createJoint(interDiv, str(i))

			if self.settings("endDeformer"):
				self.createJoint(self._centers[-1], len(self.interDiv)+1)

		else:
			for i, interDiv in enumerate(self.interDiv, start=self.start_iter):
				self.createJoint(interDiv, str(i))

		if self.settings("untwistDeformers"):
			for i, untwist in enumerate(self.unTwistDiv, start=self.start_iter):
				dfm = self.createJoint(untwist, "Untwist%s"%i)
			if self.settings("tangent") and self.settings("startDeformer"):
				dfm = self.createJoint(self.unTwistStart, "Untwist0")
			if self.settings("tangent") and self.settings("endDeformer"):
				dfm = self.createJoint(self.unTwistEnd, "Untwist%i"%(len(self.interDiv)+1))

	# --------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		if self.settings("scaleWithCurve") or self.settings("preserveLength"):
			self.crvLengthAttr = self.createSetupAttr("curveLength", "float", self.length, 0, None)

		step = 1.0 / (self.settings("interDeformers") + 1.0)
		self.scaleAttrs = [None] * 100
		for i, div in enumerate(self.interDiv, start=self.start_iter):
			u = i*step
			attr = self.createSetupAttr("Scale%s"%i, "float", 1-u, None, None)
			self.scaleAttrs[i] = attr

	# --------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Curve
		if self.settings("scaleWithCurve") or self.settings("preserveLength"):
			ciNode = self._createNode("curveInfo", "CurveInfo")
			shape = cmds.listRelatives(self.crv, shapes=True)[0]
			cmds.connectAttr(shape+".worldSpace[0]", ciNode+".inputCurve")

		align = self.axis[0]+"-z"

		if self.settings("scaleWithCurve") or self.settings("preserveLength"):
			scaleNode = self._createNode("multDoubleLinear", "LengthRescale")
			cmds.setAttr(scaleNode+".input1", self.length)
			self.connectAttr(self.scaleAttr(), (scaleNode, "input2"))

			lengthRatioNode = self._createNode("multiplyDivide", "LengthRatio")
			cmds.setAttr(lengthRatioNode+".operation", 2) # Division

			cmds.connectAttr(ciNode+".arcLength", lengthRatioNode+".input1X")
			cmds.connectAttr(scaleNode+".output", lengthRatioNode+".input2X")

			cmds.connectAttr(lengthRatioNode+".input1X", lengthRatioNode+".input2Y")
			cmds.connectAttr(lengthRatioNode+".input2X", lengthRatioNode+".input1Y")

		# Divisions
		step = 1.0 / (self.settings("interDeformers") + 1.0)
		for i, div in enumerate(self.interDiv, start=self.start_iter):
			u = i*step

			# Position
			if self.settings("parametric"):
				cns = compounds.curveConstraints(div, self.crv, axis=align, parametric=True, u=u, percentageToU=True)
			else:
				cns = compounds.curveConstraints(div, self.crv, axis=align, parametric=False, u=u)
				if self.settings("preserveLength"):
					mulNode = self._createNode("multiplyDivide", "Mul")
					cmds.setAttr(mulNode+".operation", 1) # Multiply
					cmds.setAttr(mulNode+".input1X", u)
					cmds.connectAttr(lengthRatioNode+".outputY", mulNode+".input2X")
					cmds.connectAttr(mulNode+".outputX", cns+".uValue")

			# Rotation
			if self.settings("twistMethod") == "spinePointAt":
				compounds.spinePointAt(cns, self._centers[0], self._centers[-1], blend=u, solver=1)
			else:
				compounds.pointAtBlendedAxis(cns, self._centers[0], self._centers[-1], blend=u)

			# Scaling
			if self.settings("scaleWithCurve"):
				if self.settings("negate"):
					negNode = self._createNode("multiplyDivide", "Neg")
					cmds.setAttr(negNode+".operation", 1) # Multiply
					cmds.connectAttr(lengthRatioNode+".outputX", negNode+".input1X")
					cmds.setAttr(negNode+".input2X", -1)
					cmds.connectAttr(negNode+".outputX", div+".scale"+self.axis.upper())
				else:
					cmds.connectAttr(lengthRatioNode+".outputX", div+".scale"+self.axis.upper())


			if self.settings("scaleWithControllers"):
				if self.settings("scaleWithInterControllers"):
					dt = Vector3(cmds.xform(div, q=True, worldSpace=True, translation=True))
					ct = [cmds.xform(ctr, q=True, worldSpace=True, translation=True) for ctr in self._centers]
					ct = [Vector3(x) for x in ct]

					lengths = [dt.distance(v) for v in ct]
					sortedLengths = sorted(lengths)

					refA = lengths.index(sortedLengths[0])
					refB = lengths.index(sortedLengths[1])
					refA = self._centers[refA]
					refB = self._centers[refB]

					refADmNode = self._createNode("decomposeMatrix", "DM")
					cmds.connectAttr(refA+".worldMatrix[0]", refADmNode+".inputMatrix")

					if sortedLengths[0] < 1E-6:
						divNode = self._createNode("multiplyDivide", "Div")
						cmds.setAttr(divNode+".operation", 2) # Divide
						cmds.connectAttr(refADmNode+".outputScale", divNode+".input1")
						cmds.connectAttr(self.sclAttr, divNode, "input2X")
						cmds.connectAttr(self.sclAttr, divNode, "input2Y")
						cmds.connectAttr(self.sclAttr, divNode, "input2Z")

						output = divNode
					else:
						blend = sortedLengths[1] / sum(sortedLengths[:2])

						refBDmNode = self._createNode("decomposeMatrix", "DM")
						cmds.connectAttr(refB+".worldMatrix[0]", refBDmNode+".inputMatrix")

						blendNode = self._createNode("blendColors", "Blend")
						cmds.connectAttr(self.scaleAttrs[i], blendNode, "blender")
						cmds.connectAttr(refADmNode+".outputScale", blendNode+".color1")
						cmds.connectAttr(refBDmNode+".outputScale", blendNode+".color2")

						divNode = self._createNode("multiplyDivide", "Div")
						cmds.setAttr(divNode+".operation", 2) # Divide
						cmds.connectAttr(blendNode+".output", divNode+".input1")
						cmds.connectAttr(self.sclAttr, divNode, "input2X")
						cmds.connectAttr(self.sclAttr, divNode, "input2Y")
						cmds.connectAttr(self.sclAttr, divNode, "input2Z")

						output = divNode

				else:
					refADmNode = self._createNode("decomposeMatrix", "DM")
					cmds.connectAttr(self._centers[0]+".matrix", refADmNode+".inputMatrix")
					refBDmNode = self._createNode("decomposeMatrix", "DM")
					cmds.connectAttr(self._centers[-1]+".matrix", refBDmNode+".inputMatrix")

					blendNode = self._createNode("blendColors", "Blend")
					cmds.connectAttr(self.scaleAttrs[i], blendNode+".blender")
					cmds.connectAttr(refADmNode+".outputScale", blendNode+".color1")
					cmds.connectAttr(refBDmNode+".outputScale", blendNode+".color2")

					divNode = self._createNode("multiplyDivide", "Div")
					cmds.setAttr(divNode+".operation", 1) # Multiply
					cmds.connectAttr(blendNode+".output", divNode+".input1")
					cmds.setAttr(divNode+".input2X", 1)
					cmds.setAttr(divNode+".input2Y", 1)
					cmds.setAttr(divNode+".input2Z", 1)

					output = divNode

				for s in "xyz":
					if s == self.axis:
						continue

					cmds.connectAttr(output+".output"+s.title(), div+".scale"+s.title())

		# Untwist
		if self.settings("untwistDeformers"):
			if self.settings("tangent"):
				slaves = [self.unTwistStart] + self.unTwistDiv + [self.unTwistEnd]
				masters = [self._centers[0]] + self.interDiv + [self._centers[-1]]
			else:
				slaves = self.unTwistDiv
				masters = self.interDiv
			for div,untwist in izip(masters, slaves):
				poseCnsCompound = self._createCompound("poseConstraint2", untwist, [div])

				negNode = self._createNode("unitConversion", "Negate")
				cmds.setAttr(negNode+".conversionFactor", -1)
				cmds.connectAttr(div+".rotate%s"%self.axis.title(), negNode+".input")

				cnx = ".input[0].localOffsetTransform.localOffsetRotate.localOffsetRotate%s"%self.axis.title()
				cmds.connectAttr(negNode+".output", poseCnsCompound.nodes("PoseCns")+cnx)

	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		pass
		# sbfr = self.getObject("Start", usage="Hbfr")
		# bfrs = [self.getObject("Part%s"%i, usage="Hbfr") for i in xrange(1, self.count("Part")-1)]
		# ebfr = self.getObject("End", usage="Hbfr")

		# buffers = [sbfr] + bfrs + [ebfr]
		# for i, bfr in enumerate(buffers):
		# 	self.connect_parenting(bfr, "Control1")
		# 	self.connect_constraining(bfr, "Control%s"%(i+1))