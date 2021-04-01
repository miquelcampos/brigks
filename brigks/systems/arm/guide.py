from maya import cmds

from tools.marbie.systems.systemGuide import SystemGuide

class ArmSystemGuide(SystemGuide):	

	markerNames = ("Part1", "Part2", "Part3", "Part4", "Prop")
	markerMinMax = {}

	def addSettings(self):
		self.settings["blend"] = "FK" # FK, IK

		self.settings["stretchDefault"] = 1.5
		self.settings["reverseDefault"] = 0.0

	def connectionPorts(self):
		super(ArmSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["parent", "attachToGeo", "multi", "customParent"],
			IK=["parent", "attachToGeo", "multi", "customParent"],
			UpVector=["parent", "attachToGeo", "multi", "customParent"],
			UI=["parent"],
			)

		return ports

	def connectionSlots(self):
		super(ArmSystemGuide, self).connectionSlots()

		slots = dict(
			TwUprStart=("Rig", "TwUprStart"),
			InterUpr=("Rig", "InterUpr"),
			TwUprEnd=("Rig", "TwUprEnd"),
			TwLwrStart=("Rig", "TwLwrStart"),
			InterLwr=("Rig", "InterLwr"),
			TwLwrEnd=("Rig", "TwLwrEnd"),
			Hand=("Rig", "Bone3"),
			Center=("Ctrl", "Center"),
			Prop=("Ctrl", "Prop")
			)

		return slots