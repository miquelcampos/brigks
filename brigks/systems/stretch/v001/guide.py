
from brigks.systems.systemGuide import SystemGuide


class StretchSystemGuide(SystemGuide):

	markerNames = ("Root", "End")
	markerMinMax = dict()
	
	def addSettings(self):
		self._settings["addControllers"] = False

		self._settings["twist"] = True
		self._settings["twistBlend"] = .5

		self._settings["stretch"] = True
		self._settings["stretchBlend"] = 1.0

		self._settings["squash"] = False
		self._settings["squashy"] = 1.0
		self._settings["squashz"] = 1.0

	def connectionPorts(self):
		super(StretchSystemGuide, self).connectionPorts()

		ports = dict(
			Start=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			End=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=("uiHost")
			)

		return ports

	def connectionSlots(self):
		super(StretchSystemGuide, self).connectionSlots()

		slots = dict(
			Bone=("Rig", "Bone")
			)

		return slots
