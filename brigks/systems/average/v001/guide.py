from maya import cmds

from brigks.systems.systemGuide import SystemGuide

class AverageSystemGuide(SystemGuide):	

	markerNames = ("Root",)
	markerMinMax = {}

	def addSettings(self):
		self._settings["addControllers"] = False
		self._settings["blendAnimatable"] = False

		self._settings["blend"] = .5
		self._settings["position"] = True
		self._settings["rotation"] = True
		self._settings["scaling"] = True

	def connectionPorts(self):
		super(AverageSystemGuide, self).connectionPorts()
		
		ports = dict(
			Parent=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			MasterA=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			MasterB=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(AverageSystemGuide, self).connectionSlots()

		usage = "Ctl" if self._settings("addControllers") else "Bfr"
		slots = dict(
			Average=(usage, "Average")
			)

		return slots
