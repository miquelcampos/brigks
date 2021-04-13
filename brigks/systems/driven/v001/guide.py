from maya import cmds

from brigks.systems.systemGuide import SystemGuide

class DrivenSystemGuide(SystemGuide):	

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(1,-1)
		)
	
	def addSettings(self):
		self._settings["addControllers"] = True
		self._settings["useIkColor"] = False

		self._settings["addControllers"] = False
		self._settings["addDeformerRef"] = False
		
		for i in xrange(1, self.count("Rail")+1):
			self._settings["minRot%s"%i]= -90
			self._settings["maxRot%s"%i]= 90
			self._settings["axis%s"%i]= "Z"

	def connectionPorts(self):
		super(DrivenSystemGuide, self).connectionPorts()

		ports = {}
		for i in xrange(1, self.count("Rail")+1):
			self.port["Rail%s"%i] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			self.port["RailCls%s"%i] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			self.port["RailCustom%s"%i] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			
		self.port["Reference"] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
		self.port["Tracker"] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]

		return ports

	def connectionSlots(self):
		super(DrivenSystemGuide, self).connectionSlots()

		usage = "Ctl" if self._settings("addControllers") else "Rig"
		slots = dict()
		for i in xrange(1, self.count("Rail")+1):
			slots["Part%s"%i] = (usage, "Part%s"%i)

		return slots