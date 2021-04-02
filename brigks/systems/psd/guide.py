

from brigks.systems.systemGuide import SystemGuide

class PsdSystemGuide(SystemGuide):	

	markerNames = ()
	markerMinMax = {}

	def addSettings(self):
		for i in xrange(1, self.count("Driver")+1):
			self.settings["drvName{}".format(i)] = "Driver{}".format(i)

	def connectionPorts(self):
		super(PsdSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["parent"],
			Reference=["parent", "attachToGeo", "multi", "customParent"],
			Tracker=["parent", "attachToGeo", "multi", "customParent"],
			Orientation=["parent"]
			)

		return ports

	def connectionSlots(self):
		super(PsdSystemGuide, self).connectionSlots()

		slots = dict(
			Root=("Rig", "Root"))

		return slots
		