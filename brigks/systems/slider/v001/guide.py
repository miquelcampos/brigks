from maya import cmds

from brigks.systems.systemGuide import SystemGuide

class SliderSystemGuide(SystemGuide):	

	markerNames = ("Part", "Pos", "Neg")
	markerMinMax = dict(
		Part=(1,-1),
		Pos=(1,-1),
		Neg=(1,-1)
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
			Reference=("parent"),
			Tracker=("parent"))

		for i in xrange(1, self.count("Rail")+1):
			ports["Rail{}".format(i)] = ("parent")

		return ports

	def connectionSlots(self):
		super(SliderSystemGuide, self).connectionSlots()

		usage = "Ctl" if self._settings("addControllers") else "Rig"
		slots = dict()
		for i in xrange(1, self.count("Slider")+1):
			slots["Slider{}".format(i)] = (usage, "Slider{}".format(i))

		return slots

			