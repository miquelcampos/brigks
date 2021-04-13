
from brigks.systems.systemGuide import SystemGuide


class TrackerSystemGuide(SystemGuide):

	markerNames = ()
	markerMinMax = dict()

	def addSettings(self):
		pass

	def connectionPorts(self):
		super(TrackerSystemGuide, self).connectionPorts()

		ports = dict(
			Reference=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			Tracker=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			)

		return ports

	def connectionSlots(self):
		super(TrackerSystemGuide, self).connectionSlots()
