

from brigks.systems.systemGuide import SystemGuide

class PsdSystemGuide(SystemGuide):	

	markerNames = ("Root", "Driver", "Inner", "Outer")
	markerMinMax = dict(Driver=(1,-1),
						Inner=(1,-1),
						Outer=(1,-1))

	def addSettings(self):
		for i in xrange(1, self.count("Driver")+1):
			self._settings["drvName{}".format(i)] = "Driver{}".format(i)
			self._settings["interpType{}".format(i)] = "Linear"

		self._settings["twistAxis"] = "X"
		self._settings["twistInterp"] = "Linear"
		self._settings["twistMin"] = -90
		self._settings["twistMax"] = 90
		self._settings["twistSplit"] = True

	def connectionPorts(self):
		super(PsdSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			Reference=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			Tracker=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			Orientation=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			)

		return ports

	def connectionSlots(self):
		super(PsdSystemGuide, self).connectionSlots()

		slots = dict(
			Root=("Rig", "Root"))

		return slots
		