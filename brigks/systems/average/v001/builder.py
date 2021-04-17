from maya import cmds

from math3d.transformation import Transformation

from brigks.systems.systemBuilder import SystemBuilder

class AverageSystemBuilder(SystemBuilder):

	def createObjects(self):
		# Transformation
		tfm = Transformation.lookAt(self.translations("Root"), self.directions("Root", "x"), self.directions("Root", "z"), "xz", self.negate())

		# Controller
		self.bfr = self.createBuffer(None, "Average", tfm,)

		if self.settings("addControllers"):
			self.ctl = self.createController(self.bfr, "Average", self.guide().controllers("gde_Root"), tfm, color=self.colorFk())

	def createJoints(self):
		if self.settings("addControllers"):
			self.createJoint(self.ctl, 1)
		else:
			self.createJoint(self.bfr, 1)

	# ----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		if self.settings("blendAnimatable"):
			self.blendAttr = self.createAnimAttr("Blend", "float", self.settings("blend"), 0, 1)

	# ----------------------------------------------------------------------------
	# CONNECTION
	def createConnection(self):
		bfr = self.getObject("Average", usage="Hbfr")

		# Parent
		parent = "Parent" if self.connections("Parent").settings("keyslots") else "MasterA"

		self.connect_parenting(bfr, parent)

		masterA = self.connectionObject("MasterA")
		masterB = self.connectionObject("MasterB")

		if not masterA or not masterB:
			return

		cmpd = self._createCompound("poseConstraint2", bfr, [masterA, masterB], maintainOffset=True,
													translate=self.settings("position"),
		 											rotate=self.settings("rotation"),
		 											scale=self.settings("scaling"))

		if self.settings("blendAnimatable"):
			blendAttr = self.attributes("Blend", "anim")
			cmpd.connectBlend(self.toNative(blendAttr), index=1)
		else:
			cmpd.setBlend(self.settings("blend"), index=1)