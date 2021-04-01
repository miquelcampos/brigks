from maya import cmds

from tools.marbie.systems.systemGuide import SystemGuide

class AverageSystemGuide(SystemGuide):	

	markerNames = ("Part1",)
	markerMinMax = {}

	def addSettings(self):
		self.settings["addControllers"] = False
		self.settings["blendAnimatable"] = False

		self.settings["blend"] = .5
		self.settings["position"] = True
		self.settings["rotation"] = True
		self.settings["scaling"] = True

	def connectionPorts(self):
		super(AverageSystemGuide, self).connectionPorts()
		
		ports = dict(
			Parent=["parent"],
			MasterA=["parent"],
			MasterB=["parent"],
			UI=["parent"]
			)

		return ports

	def connectionSlots(self):
		super(AverageSystemGuide, self).connectionSlots()

		usage = "Ctl" if self.settings("addControllers") else "Bfr"
		slots = dict(
			Average=(usage, "Average")
			)

		return slots
