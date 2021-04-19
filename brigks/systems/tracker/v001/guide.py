
from brigks.systems.systemGuide import SystemGuide


class TrackerSystemGuide(SystemGuide):

	markerNames = ()
	markerMinMax = dict()

	def addSettings(self):
		self._settings["driverDefOrder"] = []
		self._settings["driverDefs"] = {}

	def connectionPorts(self):
		super(TrackerSystemGuide, self).connectionPorts()

		ports = dict(
			Tracker=["rotationTracker"]
			)

		return ports

	def connectionSlots(self):
		super(TrackerSystemGuide, self).connectionSlots()
