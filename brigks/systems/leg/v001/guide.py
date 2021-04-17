
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class LegSystemGuide(SystemGuide):	

	markerNames = ("Root", "Knee", "Ankle", "Eff")
	markerPositions = dict(
		Root=Vector3([15,100,0]),
		Knee=Vector3([15,50,5]),
		Ankle=Vector3([15,10,0]),
		Eff=Vector3([15,10,5]),
		)

	def addSettings(self):
		self._settings["blend"] = "IK" # FK, IK

		self._settings["lockKneeRotation"] = False

		self._settings["stretchDefault"] = 1.5
		self._settings["reverseDefault"] = 0.0

		self._settings["ankleUpVector"] = "World Y" # World Y, Guide Z

	def connectionPorts(self):
		super(LegSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			FK=["slotParent", "meshAttach", "multiParent", "customParent"],
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