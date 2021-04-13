from maya import cmds

from brigks.systems.systemGuide import SystemGuide

class LegSystemGuide(SystemGuide):	

	markerNames = ("Root", "Knee", "Ankle", "Eff")
	markerMinMax = {}

	def addSettings(self):
		self._settings["blend"] = "FK" # FK, IK

		self._settings["stretchDefault"] = 1.5
		self._settings["reverseDefault"] = 0.0

	def connectionPorts(self):
		super(LegSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			IK=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UpVector=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"],
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