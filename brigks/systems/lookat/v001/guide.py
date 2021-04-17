from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class LookatSystemGuide(SystemGuide):

	markerNames = ("Root", "Eff")
	markerPositions = dict(
		Root=Vector3([0,10,0]),
		Eff=Vector3([0,10,10]),
		)

	def addSettings(self):
		self._settings["addLocalController"] = True
		self._settings["addTargetController"] = True
		self._settings["addUpVController"] = False
		self._settings["extraOffsetController"] = False
		self._settings["keepRotationOffset"] = False

	def connectionPorts(self):
		super(LookatSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			Eff=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UpVector=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(LookatSystemGuide, self).connectionSlots()

		slots = dict(
			Direction=("Rig", "Direction"),
			Local=("Rig", "Local")
		)

		if self._settings["extraOffsetController"]:
			slots["Offset"] = ("Rig", "Offset")

		return slots
