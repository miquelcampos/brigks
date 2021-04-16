from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import constants, attributes, create, compounds, umath

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3, Vector3Array

class SpineSystemBuilder(SystemBuilder):

	def createObjects(self):

		# SIZE
		size = self.translations("Root").distance(self.translations("Eff"))
		fkSize = size * .8
		ikSize = size *.75
		hipSize = size * 1.25

		# TRANSFORMATION
		normal = self.directions("Root", "z")
		
		positions = []
		transforms = []

		for i in range(self.ctl_count):
			lookat = self.translations("Eff") - self.translations("Root")
			t = transformation.lookAt(self.translations("Root"), lookat, normal, self.settings("axis").lower(), self.negate())
			t.translation = self.translations("Root").lerp(self.translations("Eff"), i/(self.ctl_count-1.0))
			positions.append(t.translation)
			transforms.append(t)

		# OBJECTS
		self.root = self.createRig(None, "Root")

		# Curves
		points = [positions[i] for i in [0,2,2,4]]
		self.crvA = create.curve("CrvA", points, closed=False, degree=3, parent=self.root)

		points = [positions[0].lerp(positions[-1], i/6.0) for i in xrange(7)]
		self.crvB = create.bezier("CrvB", self.root, points)
		
		# Controllers
		self.fkCtl = []
		self.hookRig = []
		fk_parent = self.root
		self.ikBfr = []
		self.ikCtl = []
		self.hookRig = []
		for i, tfm in enumerate(transforms, start=1):
			
			# Fk Controllers
			fkCtl = self.createController(fk_parent, "Fk%s"%i, tfm, "sphere", size=fkSize, so=(1,0,1), color=self.colorFk())
			# self.setInversedsettings(fkCtl, ["posx", "rotz", "roty"])
			attributes.setRotOrder(fkCtl, "XYZ")
			
			fk_parent = fkCtl
			self.fkCtl.append(fkCtl)
			
			# Ik Controllers
			ikBfr = self.createBuffer(self.root, "Ik%s"%i, tfm)
			self.ikBfr.append(ikBfr)
			

			# First ik ctl is a box
			if i in [1,5]:
				ikCtl = self.createController(ikBfr, "Ik%s"%i, tfm, "cube", size=hipSize, so=(1,.25,1), color=self.colorIk())
			else:
				ikCtl = self.createController(ikBfr, "Ik%s"%i, tfm, "sphere", size=ikSize, so=(1,0,1), color=self.colorIk())
			
			# if i in [2,4]:
			# 	self.addToSubControllers(ikCtl)

			# self.setInversedsettings(ikCtl, ["posx", "rotz", "roty"])
			attributes.setRotOrder(ikCtl, "YZX")

			self.ikCtl.append(ikCtl)

			# Hooks
			if i == 1:
				hookRig = None
			else:
				hookRig = self.createRig(self.root, "Hook%s"%i, tfm, "cube", size=2)
			self.hookRig.append(hookRig)

		# Tangent parents
		self.aTan0 = self.createRig(self.ikCtl[0], "ATan0", transforms[2], "pyramid", size=.5)
		self.aTan1 = self.createRig(self.ikCtl[-1], "ATan1", transforms[2], "pyramid", size=.5)

		self.bTan0 = self.createRig(self.ikCtl[0], "BTan0", transforms[1], "pyramid", size=.5)
		self.bTan1 = self.createRig(self.ikCtl[2], "BTan1", transforms[1], "pyramid", size=.5)
		self.bTan2 = self.createRig(self.ikCtl[2], "BTan2", transforms[2], "pyramid", size=.5)
		self.bTan3 = self.createRig(self.ikCtl[2], "BTan3", transforms[3], "pyramid", size=.5)
		self.bTan4 = self.createRig(self.ikCtl[4], "BTan4", transforms[3], "pyramid", size=.5)
		
		if self.settings("breathing"):
			breathBfr = self.createBuffer(self.hookRig[4], "Breathing", transforms[-1])
			self.breathCtl = self.createController(breathBfr, "Breathing", transforms[-1], "cube", size=ikSize, color=self.colorIk())
			# self.addToSubControllers(self.breathCtl)
			# self.setInversedsettings(self.breathCtl, ["posx", "rotz", "roty"])
			attributes.setRotOrder(self.breathCtl, "YZX")

	def createJoints(self):
		self.createJoint(self.ikCtl[0], "1")
		self.createJoint(self.hookRig[2], "3")
		if self.settings("breathing"):
			self.createJoint(self.breathCtl, "5")
		else:
			self.createJoint(self.hookRig[4], "5")
	
	#----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.blendAttr = self.createAnimAttr("Blend", "float", self.settings("blend") == "IK", 0, 1)
		self.showCtrlAttr = self.createAnimAttr("showCtrl", "bool", False) 
		
	def createLayout(self): 
		pass
		
	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		# Visibilities
		fkCompare = compounds.compare("compare", self.blendAttr, 1, "<")
		ikCompare = compounds.compare("compare", self.blendAttr, 0, ">")
		
		cmds.connectAttr(self.showCtrlAttr, fkCompare+".colorIfFalseR")
		cmds.connectAttr(self.showCtrlAttr, ikCompare+".colorIfFalseR")

		for ctl in self.fkCtl:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(fkCompare+"outputColorR", shp+".visibility")

		for ctl in self.ikCtl[1:]:
			for shp in cmds.listRelatives(ctl, shapes=True):
				cmds.connectAttr(ikCompare+"outputColorR", shp+".visibility")

		# Cluster Centers
		compounds.pointCenter(self.crvA, self.ikCtl[0], 0)
		compounds.pointCenter(self.crvA, self.aTan0, 1)
		compounds.pointCenter(self.crvA, self.aTan1, 2)
		compounds.pointCenter(self.crvA, self.ikCtl[4], 3)

		compounds.pointCenter(self.crvB, self.ikCtl[0], 0)
		compounds.pointCenter(self.crvB, self.bTan0, 1)
		compounds.pointCenter(self.crvB, self.bTan1, 2)
		compounds.pointCenter(self.crvB, self.bTan2, 3)
		compounds.pointCenter(self.crvB, self.bTan3, 4)
		compounds.pointCenter(self.crvB, self.bTan4, 5)
		compounds.pointCenter(self.crvB, self.ikCtl[4], 6)

		# Hooks
		for hookRig, fkCtl, ikCtl in izip(self.hookRig, self.fkCtl, self.ikCtl):
			
			if hookRig is None:
				continue

			cns = self._createCompound("PoseConstraint", hookRig, [ikCtl, fkCtl])
			cns.connectBlend(self.blendAttr())
		
		# Mid Ik Controller
		axis = self.settings("axis").lower()
		axis = axis[0] + "-"+ axis[-1]
		cns = compounds.curveConstraint(self.ikBfr[2], self.crvA, axis=axis, parametric=True, u=.5)
		compounds.spinePointAt(cns, self.ikCtl[0], self.ikCtl[4], blend=.5, solver=1) 

		cns = compounds.curveConstraint(self.ikBfr[1], self.crvB, axis=axis, parametric=False, u=.25)
		compounds.spinePointAt(cns, self.ikCtl[0], self.ikCtl[2], blend=.5, solver=1) 

		cns = compounds.curveConstraint(self.ikBfr[3], self.crvB, axis=axis, parametric=False, u=.75)
		compounds.spinePointAt(cns, self.ikCtl[2], self.ikCtl[4], blend=.5, solver=1) 

	
	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		root = self.getObject("Root")
		self.connect_parenting(root, "Root")
		
		