from brigks.systems.systemBuilder import SystemBuilder

from math3d.transformation import Transformation
from math3d.vectorN import Vector3

class ChainSystemBuilder(SystemBuilder):
	
	def createObjects(self):
		# Settings
		self.isFk = "FK" in self.settings()["kinematic"]
		self.isIk = "IK" in self.settings()["kinematic"]
		self.isFkIk = self.isFk and self.isIk
		
		# TRANSFORMATION
		# Normal
		if self.count("Part") > 2:
			normal = Vector3.planeNormal(self.translations("Part")[:3])
			if normal.length() < 1E-6:
				normal = self.gdir("Part1").z
			if self.negate(): 
				normal *= -1
		else:
			normal = self.gdir("Part1").z

		boneTfm = Transformation.chain(self.translations("Part"), normal, axis="xz", negativeSide=self.negate())
		boneLen = Vector3.distances(self.translations("Part"))

		self.setSettings(dict(
			count=len(boneLen),
			lengths=boneLen))
		
		if self.settings()["setNeutralPose"]:
			bfrTfm = boneTfm
		else:
			bfrTfm = [tfm.copy(rotation=boneTfm[max(i-1,0)].quaternion) for i, tfm in enumerate(boneTfm)]
		
		if self.isIk:
			ikTfm = boneTfm[-1].copy(translation=self.translations("Part")[-1])
			
			# Up Vector
			if self.guide().count("Part") > 2:
				upvTfm = Transform(translation=Vector.UpVector(self.translations()[0], self.translations()[2], normal, ratio=1, negate=self.negate()))
			else:
				upvTfm = Transform(translation=Vector.UpVector(self.translations()[0], self.translations()[1], normal, ratio=1, negate=self.negate()))
			

		if self.settings()["dynamic"]:
			tgtTfm = boneTfm[1:]
			tgtTfm.append(boneTfm[-1].copy(translation=self.translations("Part")[-1]))
			

		# OBJECTS

		# Root
		self._root = self.addNull(None, "Root", tfm=boneTfm[0])
		
		# FK Controllers -----------------------------------------
		if self.isFk:
			self.fkBfr = []
			self.fkCtl = []
			self.fkDir = []
			parent = self._root
			for i, (tfm, btfm, dist) in enumerate(izip(boneTfm, bfrTfm, boneLen), start=1):
				
				fkBfr = self.addBfr(parent, "Fk%s"%i, tfm=btfm)
				fkCtl = self.addCtl(fkBfr, "Fk%s"%i, tfm, "sphere", so=[0,1,1], color=self.colorFk())
										  
				self.setInversedParameters(fkCtl, middle=["posz", "rotx", "roty"])
				self.setRotOrder(fkCtl, self.settings()["defaultRotationOrder"])

				parent = fkCtl

				self.fkBfr.append(fkBfr)
				self.fkCtl.append(fkCtl)

				bone = self.addNull(fkCtl, "Dir%s"%i, tfm, "pyramid", size=1, ro=[0,0,-90], so=[.5,self.factor()*dist,.5])

				self.fkDir.append(bone)

			# Add the end reference for ikfk matching
			tfm = boneTfm[-1].copy(translation=self.translations()[-1])
			self._tip = self.addNull(self.fkCtl[-1], "Tip", tfm)
				
		# IK Controllers --------------------------------------
		if self.isIk:
			# Ik Controller
			self.ikBfr = self.addBfr(self._root, "Ik", tfm=ikTfm)
			self.ikCtl = self.addCtl(self.ikBfr, "Ik", ikTfm, "cube",  size=2, color=self.colorIk())
			self.setKeyables(self.ikCtl, constants.tr_attrs)
			self.setInversedParameters(self.ikCtl, middle=["posz", "rotx", "roty"])

			# UpVector Controller
			self.upvBfr = self.addBfr(self._root, "upv", upvTfm)
			self.upvCtl = self.addCtl(self.upvBfr, "upv", upvTfm, "diamond", color=self.colorIk())
			self.setKeyables(self.upvCtl, constants.t_attrs)
			self.setInversedParameters(self.upvCtl, middle=["posz"])

			# Ik Chain
			# if self.negate(): # Yeah we're undoing the normal negation, but we shouldn't have it here.
			# 	normal *= -1
			self.ikChn = self.addChain(self._root, "Ik", self.translations("Part"), normal, self.negate())
			
			self.upvCrv = self.addCnsCurve([self.ikChn.root(), self.upvCtl, self.ikChn.effector()], "UpvCrv")
			# self.addToGroup(self.upvCrv, "Unselectable")

		# Bones -------------------------------
		if self.isFkIk:# or (self.isFk and self.settings()["dynamic"]):
			self.bones = []
			parent = self._root
			for i, (tfm, dist) in enumerate(izip(boneTfm, boneLen), start=1):
				
				bone = self.addNull(parent, "Bone%s"%i, tfm, "cube", size=1, po=[self.factor()*dist*.5,0,0], so=[dist,.5,.5])
				# self.setNeutralPose(bone, dcc.constants.siTrn)
				
				self.bones.append(bone)
				parent = bone

			# if self.settings()["setNeutralPose"]:
			# 	for bone in self.bones:
					# self.setNeutralPose(bone)
		elif self.isFk:
			self.bones = self.fkCtl
		else:
			self.bones = self.ikChn.bones()

		# Dynamic ----------------------------
		if self.settings()["dynamic"]:
			self.dfmHost = []
			self.dynCns = []
			self.target = []
			self.harmonic = []
			self.dynBone = []
			parent = self._root
			for i, (bone, tfmA, tfmB) in enumerate(izip(self.bones, boneTfm, tgtTfm), start=1):

				dynCns = self.addNull(parent, "DynCns%s"%i, tfmA, "cube", size=1)
				self.dynCns.append(dynCns)
				target = self.addNull(dynCns, "Target%s"%i, tfmB, "null", size=1)
				self.target.append(target)
				harmonic = self.addNull(target, "Harmonic%s"%i, tfmB, "diamond", size=1)
				self.harmonic.append(harmonic)
			
				dynBone = self.addNull(parent, "Dynamic%s"%i, tfmA, "pyramid", size=1, ro=[0,0,-90], so=[1,self.factor(),1])
				self.dynBone.append(dynBone)
				parent = dynBone
				self.dfmHost.append(dynBone)
		else:
			self.dfmHost = self.bones


		# Strap ----------------------------
		if self.settings()["strap"]:
			endTfm = boneTfm[-1].copy(translation=self.translations()[-1])
			self.end = self.addNull(self.dfmHost[-1], "End", endTfm)

	def createDeformers(self):
		centers = [self.addDeformer(master, i) for i, master in enumerate(self.dfmHost, start=1)]
			
		# Strap ----------------------------
		if self.settings()["strap"]:
			centers.append(self.addDeformer(self.end, "End"))

			surface = self.addCnsSurface(centers, "Strap", width=self.size(), tangent=.25)
		 	self.addSurfaceDeformers(surface, self.settings()["strapDeformers"])

	#----------------------------------------------------------------------------
	# PROPERTIES 
	def createAttributes(self):
		if self.isFkIk:
			self.blendAttr = self.addAnimAttr("Blend", "float", self.settings()["blend"]=="IK", 0, 1)
			self.showCtrlAttr = self.addAnimAttr("showCtrl", "bool", False) 

			self.addSetupAttr("Count", "int", len(self.fkCtl))
		
		if self.isIk:
			self.rollAttr = self.addAnimAttr("roll", "float", 0, -180, 180)

		if self.settings()["dynamic"]:
			self.dynamicAttr = self.addAnimAttr("dynamic", "bool", self.settings()["dynActive"])
			self.globalAmplitudeAttr = self.addAnimAttr("globalAmplitude", "float", self.settings()["amplitude"], 0, 5)
			self.localAmplitudeAttr = [self.addAnimAttr("localAmplitude%s"%i, "float", 1, 0, 10) for i in xrange(1, self.guide().count("Part"))]
			
			if self.settings()["dynamicAnimatable"]:
				self.axisAttr = self.addAnimAttr("axis", "vector", (self.settings()["amplitudeX"], self.settings()["amplitudeY"], self.settings()["amplitudeZ"]))
				self.decayAttr = self.addAnimAttr("decay", "float", self.settings()["decay"], 0, 10)
				self.terminationAttr = self.addAnimAttr("termination", "float", self.settings()["termination"], 0, 1)
				self.frequencyAttr = self.addAnimAttr("frequency", "float", self.settings()["frequency"], 0, 1)
		
	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibilities
		if self.isFkIk:
			fkCompare = self._createCompound("compare", self.blendAttr, 1, "<")
			ikCompare = self._createCompound("compare", self.blendAttr, 0, ">")

			self._connectAttr(self.showCtrlAttr, (fkCompare.nodes("Cond"), "colorIfFalseR"))
			self._connectAttr(self.showCtrlAttr, (ikCompare.nodes("Cond"), "colorIfFalseR"))

			for ctl in self.fkCtl:
				for shp in ctl.activePrimitives():
					fkCompare.connectResult((shp(), "visibility"))

			for ctl in [self.ikCtl, self.upvCtl, self.upvCrv]:
				for shp in ctl.activePrimitives():
					ikCompare.connectResult((shp(), "visibility"))

		# IK Chain
		if self.isIk:
			# Constraint and up vector
			self.ikChn.setUpVector(self.upvCtl)
			self.ikChn.connectRoll(self.rollAttr)
			self.ikChn.setHandleMaster(self.ikCtl)

		if self.isFk:
			for i, (fkBone, fkCtl) in enumerate(izip(self.fkDir, self.fkCtl)):
				slave = fkBone
				upMaster = fkCtl
				axis = self.sign()+"xy"
				if i < (len(self.bones)-1):
					master = self.fkCtl[i+1]
				else:
					master = self._tip
					
				self._createCompound("AimConstraint", slave, master, axis=axis, upMaster=upMaster, upVector=om.MVector(0,1,0))
				
		# 	# Scaling
		# 	for bfr in self.fkBfr[1:]:
		# 		for s in "xyz":
		# 			sclAttr = bfr().Parameters("scl"+s)
		# 			self.addExpression(None, sclAttr, "1 / %s"%bfr().Parent.Parameters("scl"+s).FullName)

		# # Bones -----------------------------------------
		if self.isFkIk:# or (self.isFk and self.settings()["dynamic"]):
			for i, (bone, fkDir, ikBone) in enumerate(izip(self.bones, self.fkDir, self.ikChn.bones())):
				slave = bone
				masters = [fkDir, ikBone]

				cns = self._createCompound("PoseConstraint2", slave, masters)
				cns.connectBlend(self.toNative(self.blendAttr), 1)

					
		if self.settings()["dynamic"]:
			for i, (harmonic, target, dynCns, dynBone, bone) in enumerate(izip(self.harmonic, self.target, self.dynCns, self.dynBone, self.bones)):
				cns = self._createCompound("Harmonics", harmonic, target, 
					amplitude=1.0, 
					decay=self.settings()["decay"], 
					frequency=self.settings()["frequency"], 
					termination=self.settings()["termination"],
					amplitudeAxis=(self.settings()["amplitudeX"], self.settings()["amplitudeY"], self.settings()["amplitudeZ"]) )

				if i%3 == 0:
					mulNode = self._createNode("multiplyDivide", "amplitudeGlobal{}".format(i))
					self._connectAttr(self.globalAmplitudeAttr, (mulNode, "input1X"))
					self._connectAttr(self.globalAmplitudeAttr, (mulNode, "input1Y"))
					self._connectAttr(self.globalAmplitudeAttr, (mulNode, "input1Z"))

					activeNode = self._createNode("multiplyDivide", "active{}".format(i))
					self._connectAttr((mulNode, "output"), (activeNode, "input1"))
					self._connectAttr(self.dynamicAttr, (activeNode, "input2X"))
					self._connectAttr(self.dynamicAttr, (activeNode, "input2Y"))
					self._connectAttr(self.dynamicAttr, (activeNode, "input2Z"))

				axis = "XYZ"[i%3]
				self._connectAttr(self.localAmplitudeAttr[i], (mulNode, "input2"+axis))
				cns.connectAmplitude((activeNode, "output"+axis))

				if self.settings()["dynamicAnimatable"]:
					cns.connectAxis(self.toNative(self.axisAttr))
					cns.connectDecay(self.toNative(self.decayAttr))
					cns.connectTermination(self.toNative(self.terminationAttr))
					cns.connectFrequency(self.toNative(self.frequencyAttr))

				cns = self._createCompound("AimConstraint", dynBone, harmonic, axis=self.sign()+"xy", upMaster=dynCns, upVector=om.MVector(0,1,0), maintainOffset=False)
				cns = self._createCompound("PoseConstraint2", dynCns, [bone], translate=False, rotate=True, scale=False)

 
		
	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		root = self.getObject("Root")

		if self.settings()["connectionType"] == "standard":
			self.connect_parenting(root, "Root")

			# Fk Ref
			fk1Bfr = self.getObject("Fk1", "Hbfr")
			if fk1Bfr:
				self.connect_orientation(fk1Bfr, "FkRef", paramName="FkRef")

			#UpV
			if "IK" in self.settings()["kinematic"]:
				upvBfr = self.getObject("upv", "Hbfr")
				upvRef = "UpVector" if self.connectionObject("UpVector") else "Root"
				self.connect_parenting(upvBfr, upvRef)

				ikBfr = self.getObject("Ik", "Hbfr")
				ikRef = "Effector" if self.connectionObject("Effector") else "Root"
				self.connect_parenting(ikBfr, ikRef)

		else:
			self.connect_object2Cluster(root, "RootCls")
