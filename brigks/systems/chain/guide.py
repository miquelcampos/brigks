
from brigks.systems.systemGuide import SystemGuide


class ChainSystemGuide(SystemGuide):

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(2,-1)
		)

	def addSettings(self):

		self.settings["orientation"] = "Auto"  # Auto, Guide

		self.settings["kinematic"] = "FK"  # FK, IK or FK/IK
		self.settings["blend"] = "FK"

		self.settings["setNeutralPose"] = True
		self.settings["defaultRotationOrder"] = "XYZ"

		self.settings["strap"] = False
		self.settings["strapDeformers"] = 5

		self.settings["dynamic"] = False
		self.settings["dynActive"] = False
		self.settings["amplitude"] = 1.0

		self.settings["amplitudeX"] = 1.0
		self.settings["amplitudeY"] = 1.0
		self.settings["amplitudeZ"] = 1.0
		self.settings["decay"] = 8.0
		self.settings["frequency"] = .25
		self.settings["termination"] = 0.0

		self.settings["dynamicAnimatable"] = False

	def connectionPorts(self):
		super(ChainSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["parent", "attachToGeo", "multi", "customParent"],
			FkRef=["parent", "attachToGeo", "multi", "customParent"],
			IK=["parent", "attachToGeo", "multi", "customParent"],
			UpVector=["parent", "attachToGeo", "multi", "customParent"],
			UI=["parent"],
			)

		return ports

	def connectionSlots(self):
		super(ChainSystemGuide, self).connectionSlots()

		if self.settings["dynamic"]:
			usage = "Rig"
			name = "Dynamic{}"
		elif self.settings["kinematic"] == "FK/IK":
			usage = "Rig"
			name = "Bone{}"
		elif self.settings["kinematic"] == "FK":
			usage = "Ctrl"
			name = "Fk{}"
		else:
			usage = "Rig"
			name = "Ik{02d}"

		slots = dict()
		for i in xrange(1, self.count("Part")):
			slots["Bone{}".format(i)] = (usage, name.format(i))

		return slots
