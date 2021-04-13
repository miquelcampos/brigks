
from brigks.systems.systemGuide import SystemGuide


class ZlegSystemGuide(SystemGuide):	

	markerNames = ("Part1", "Part2", "Part3", "Part4", "Part5")
	markerMinMax = dict()

	def addSettings(self):
		self._settings["blend"] = "FK" # FK, IK

		self._settings["stretchDefault"] = 1.5
		self._settings["reverseDefault"] = 0.0

	def connectionPorts(self):
		super(ZlegSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			IK=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UpVector=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"],
			)

		return ports

	def connectionSlots(self):
		super(ZlegSystemGuide, self).connectionSlots()

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