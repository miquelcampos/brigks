
from tools.marbie.systems.systemGuide import SystemGuide


class QuadrantSystemGuide(SystemGuide):	

	markerNames = ("Part1",)
	markerMinMax = {}

	def addSettings(self):
		self.settings["north"] = True
		self.settings["south"] = True
		self.settings["east"] = True
		self.settings["west"] = True

		self.settings["push"] = 2.0

		self.settings["customLabel"] = False
		self.settings["label"] = "Label"
		self.settings["labelPosition"] = "North"

	def connectionPorts(self):
		super(QuadrantSystemGuide, self).connectionPorts()

		ports = dict(
			Root=("parent,")
			)

		return ports

	def connectionSlots(self):
		super(QuadrantSystemGuide, self).connectionSlots()

		slots = dict(
			Ctl=("Ctl", "Part1")
			)

		return slots
