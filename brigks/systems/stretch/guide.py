
from tools.marbie.systems.systemGuide import SystemGuide


class StretchSystemGuide(SystemGuide):

	markerNames = ("Part1", "Part2")
	markerMinMax = dict()
	
	def addSettings(self):
		self.settings["addControllers"] = False

		self.settings["twist"] = True
		self.settings["twistBlend"] = .5

		self.settings["stretch"] = True
		self.settings["stretchBlend"] = 1.0

		self.settings["squash"] = False
		self.settings["squashy"] = 1.0
		self.settings["squashz"] = 1.0

	def connectionPorts(self):
		super(StretchSystemGuide, self).connectionPorts()

		ports = dict(
			Start=("parent"),
			End=("parent"),
			UI=("parent")
			)

		return ports

	def connectionSlots(self):
		super(StretchSystemGuide, self).connectionSlots()

		slots = dict(
			Bone=("Rig", "Bone")
			)

		return slots
