
from brigks.systems.systemGuide import SystemGuide


class NeckSystemGuide(SystemGuide):

	markerNames = ("Root", "Head", "Eff")
	markerMinMax = {}

	def addSettings(self):
		self._settings["blend"] = "IK" # FK, IK

		self._settings["stretch"] = 0.0
		self._settings["orientToWorld"] = False

	def connectionPorts(self):
		super(NeckSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			IkRef=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			OriRef=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=("uiHost")
		)

		return ports

	def connectionSlots(self):
		super(NeckSystemGuide, self).connectionSlots()

		slots = {}
		for i, s in enumerate(["Root", "Mid", "Head"], start=1):
			slots[s] = ("Rig", "Hook%s"%i)

		return slots
