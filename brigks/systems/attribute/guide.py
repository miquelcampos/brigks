
from brigks.systems.systemGuide import SystemGuide


class AttributeSystemGuide(SystemGuide):

	markerNames = ()
	markerMinMax = {}

	def addSettings(self):
		self._settings["order"] = []
		self._settings["definition"] = {}

	def connectionPorts(self):
		super(AttributeSystemGuide, self).connectionPorts()

		ports = dict(
			UI=("parent,")
			)

		return ports

	def connectionSlots(self):
		super(AttributeSystemGuide, self).connectionSlots()
