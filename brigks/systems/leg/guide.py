from maya import cmds

from tools.marbie.systems.systemGuide import SystemGuide

class LegSystemGuide(SystemGuide):	

	markerNames = ("Part1", "Part2", "Part3", "Part4")
	markerMinMax = {}

	def addSettings(self):
		self.settings["blend"] = "FK" # FK, IK

		self.settings["stretchDefault"] = 1.5
		self.settings["reverseDefault"] = 0.0

	def connectionPorts(self):
		super(LegSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["parent", "attachToGeo", "multi", "customParent"],
			IK=["parent", "attachToGeo", "multi", "customParent"],
			UpVector=["parent", "attachToGeo", "multi", "customParent"],
			UI=["parent"],
			)

		return ports

	def connectionSlots(self):
		super(LegSystemGuide, self).connectionSlots()

		slots = dict(
			TwUprStart=("Rig", "TwUprStart"),
			InterUpr=("Rig", "InterUpr"),
			TwUprEnd=("Rig", "TwUprEnd"),
			TwLwrStart=("Rig", "TwLwrStart"),
			InterLwr=("Rig", "InterLwr"),
			TwLwrEnd=("Rig", "TwLwrEnd"),
			Foot=("Rig", "Bone3"),
			Center=("Ctrl", "Center"),
			)

		return slots