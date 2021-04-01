
from tools.marbie.systems.systemGuide import SystemGuide


class TrackerSystemGuide(SystemGuide):

	markerNames = ()
	markerMinMax = dict()

	def addSettings(self):
		pass

	def connectionPorts(self):
		super(TrackerSystemGuide, self).connectionPorts()

		ports = dict(
			Reference=("parent"),
			Tracker=("parent")
			)

		return ports

	def connectionSlots(self):
		super(TrackerSystemGuide, self).connectionSlots()
