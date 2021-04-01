from maya import cmds

from tools.marbie.systems.systemGuide import SystemGuide

class SliderSystemGuide(SystemGuide):	

	markerNames = ("Part", "Pos", "Neg")
	markerMinMax = dict(
		Part=(1,-1),
		Pos=(1,-1),
		Neg=(1,-1)
		)

	def addSettings(self):
		self.settings["addControllers"] = False

		for i in xrange(1, self.count("Rail")+1):
			self.settings["minRot{}".format(i)] = -90
			self.settings["maxRot{}".format(i)] = 90
			self.settings["axis{}".format(i)] = "Z"

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

		usage = "Ctl" if self.settings("addControllers") else "Rig"
		slots = dict()
		for i in xrange(1, self.count("Slider")+1):
			slots["Slider{}".format(i)] = (usage, "Slider{}".format(i))

		return slots

			