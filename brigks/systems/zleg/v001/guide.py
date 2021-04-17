from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class ZlegSystemGuide(SystemGuide):	

	markerNames = ("Root", "Knee", "Ankle", "Toe", "Eff")
	markerPositions = dict(
		Root=Vector3([15,100,0]),
		Knee=Vector3([15,50,5]),
		Ankle=Vector3([15,20,-2]),
		Toe=Vector3([15,10,0]),
		Eff=Vector3([15,10,5]),
		)

	def addSettings(self):
		self._settings["blend"] = "FK" # FK, IK

		self._settings["stretchDefault"] = 1.5
		self._settings["reverseDefault"] = 0.0

	def connectionPorts(self):
		super(ZlegSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			FK=["slotParent", "meshAttach", "multiParent", "customParent"],
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