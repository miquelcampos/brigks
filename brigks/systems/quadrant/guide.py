
from brigks.systems.systemGuide import SystemGuide


class QuadrantSystemGuide(SystemGuide):	

	markerNames = ("Part1",)
	markerMinMax = {}

	def addSettings(self):
		self._settings["north"] = True
		self._settings["south"] = True
		self._settings["east"] = True
		self._settings["west"] = True

		self._settings["push"] = 2.0

		self._settings["customLabel"] = False
		self._settings["label"] = "Label"
		self._settings["labelPosition"] = "North"

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
