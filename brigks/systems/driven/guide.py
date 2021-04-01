from maya import cmds

from tools.marbie.systems.systemGuide import SystemGuide

class DrivenSystemGuide(SystemGuide):	

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(1,-1)
		)
	
	def addSettings(self):
		self.settings["addControllers"] = True
		self.settings["useIkColor"] = False

		self.settings["addControllers"] = False
		self.settings["addDeformerRef"] = False
		
		for i in xrange(1, self.count("Rail")+1):
			self.settings["minRot%s"%i]= -90
			self.settings["maxRot%s"%i]= 90
			self.settings["axis%s"%i]= "Z"

	def connectionPorts(self):
		super(DrivenSystemGuide, self).connectionPorts()

		ports = {}
		for i in xrange(1, self.count("Rail")+1):
			self.port["Rail%s"%i] = ["parent", "attachToGeo", "multi", "customParent"]
			self.port["RailCls%s"%i] = ["parent", "attachToGeo", "multi", "customParent"]
			self.port["RailCustom%s"%i] = ["parent", "attachToGeo", "multi", "customParent"]
			
		self.port["Reference"] = ["parent", "attachToGeo", "multi", "customParent"]
		self.port["Tracker"] = ["parent", "attachToGeo", "multi", "customParent"]

		return ports

	def connectionSlots(self):
		super(DrivenSystemGuide, self).connectionSlots()

		usage = "Ctl" if self.settings("addControllers") else "Rig"
		slots = dict()
		for i in xrange(1, self.count("Rail")+1):
			slots["Part%s"%i] = (usage, "Part%s"%i)

		return slots