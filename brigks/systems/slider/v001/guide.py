from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class SliderSystemGuide(SystemGuide):	

	markerNames = ("Rail", "Pos", "Neg")
	markerMinMax = dict(
		Rail=(1,-1),
		Pos=(1,-1),
		Neg=(1,-1)
		)
	markerPositions = dict(
		Rail1=Vector3([0,0,0]),
		Pos1=Vector3([0,0,2]),
		Neg1=Vector3([0,0,-1]),
		)

	def addSettings(self):
		self._settings["addControllers"] = False

		for i in xrange(1, self.count("Rail")+1):
			self._settings["minRot{}".format(i)] = -90
			self._settings["maxRot{}".format(i)] = 90
			self._settings["axis{}".format(i)] = "Z"

	def connectionPorts(self):
		super(SliderSystemGuide, self).connectionPorts()
		
		ports = dict(
			Tracker=["rotationTracker"]
			)

		for i in xrange(1, self.count("Rail")+1):
			ports["Rail{}".format(i)] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]

		return ports

	def connectionSlots(self):
		super(SliderSystemGuide, self).connectionSlots()

		usage = config.USE_CTL if self.settings("addControllers") else config.USE_RIG
		slots = dict()
		for i in xrange(1, self.count("Rail")+1):
			slots["Slider{}".format(i)] = (usage, "Slider{}".format(i))

		return slots

			