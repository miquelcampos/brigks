from maya import cmds

from math3d import Vector3

from brigks.systems.systemBuilder import SystemBuilder

class ArmSystemBuilder(SystemBuilder):

	# def computeTransforms(self):

	# 	# TRANSFORMATIONS
	# 	markers = self.guide.markers["Part1"], self.guide.markers["Part2"], self.guide.markers["Part3"]
	# 	positions = [m.translation() for m in markers]

	# 	normal = Vector3.PlaneNormal(positions)
	# 	oriNormal = normal.copy()
	# 	if self.negate():
	# 		normal *= -1
		
	# 	# distances
	# 	self.lengths = Vector3.distances(self.gpos()[:3])
	# 	self.lengths.append(1)
	# 	ratio = self.lengths[0] / sum(self.lengths[:2])

	def createObjects(self):

		twUprStart = self.createRig(None, "TwUprStart", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		interUpr = self.createRig(None, "InterUpr", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		twUprEnd = self.createRig(None, "TwUprEnd", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		twLwrStart = self.createRig(None, "TwLwrStart", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		interLwr = self.createRig(None, "InterLwr", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		twLwrEnd = self.createRig(None, "TwLwrEnd", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		bone3 = self.createRig(None, "Bone3", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)

		center = self.createController(None, "Center", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		prop = self.createController(None, "Prop", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
