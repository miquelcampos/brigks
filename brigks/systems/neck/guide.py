
from brigks.systems.systemGuide import SystemGuide


class NeckSystemGuide(SystemGuide):

	markerNames = ("Part1", "Part2", "Part3")
	markerMinMax = {}

	def addSettings(self):
		self.settings["blend"] = "IK" # FK, IK

		self.settings["stretch"] = 0.0
		self.settings["orientToWorld"] = False

	def connectionPorts(self):
		super(NeckSystemGuide, self).connectionPorts()

		ports = dict(
			Root=("parent"),
			IkRef=("parent"),
			OriRef=("parent"),
			UI=("parent")
		)

		return ports

	def connectionSlots(self):
		super(NeckSystemGuide, self).connectionSlots()

		slots = {}
		for i, s in enumerate(["Root", "Mid", "Head"], start=1):
			slots[s] = ("Rig", "Hook%s"%i)

		return slots
