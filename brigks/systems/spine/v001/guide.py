from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class SpineSystemGuide(SystemGuide):

	markerNames = ("Root", "Eff")
	markerPositions = dict(
		Root=Vector3([0,100,0]),
		Eff=Vector3([0,135,0]),
		)

	def addSettings(self):
		self._settings["blend"] = "IK" # FK, IK
		self._settings["breathing"] = False
		self._settings["axis"] = "YZ"


	def connectionPorts(self):
		super(SpineSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"])

		return ports

	def connectionSlots(self):
		super(SpineSystemGuide, self).connectionSlots()

		slots = dict(
			Pelvis=("Ctl", "Ik1"),
			Lower=("Rig", "Hook2"),
			Middle=("Rig", "Hook3"),
			Upper=("Rig", "Hook4"),
			Chest=("Rig", "Hook5"),
			Breathing=("Ctl", "Breathing")
			)

		return slots
