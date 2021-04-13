
from brigks.systems.systemGuide import SystemGuide


class TwistSystemGuide(SystemGuide):	

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(2,-1)
		)

	def addSettings(self):
		self._settings["axis"] = "X" # (X, Y)
		
		self._settings["startDeformer"] = False
		self._settings["interDeformers"] = 3
		self._settings["endDeformer"] = False
		self._settings["untwistDeformers"] = False
		
		self._settings["startController"] = False
		self._settings["interControllers"] = True
		self._settings["endController"] = False
		
		self._settings["scaleWithCurve"] = False
		self._settings["scaleWithControllers"] = False
		self._settings["scaleWithInterControllers"] = False
		
		self._settings["parametric"] = True
		self._settings["preserveLength"] = False
		self._settings["tangent"] = True
		self._settings["tangentDistance"] = .25 
		self._settings["pushCurvePoints"] = False 

	def connectionPorts(self):
		super(TwistSystemGuide, self).connectionPorts()
		
		ports = {}
		for i in xrange(1, self.count("Part")+1):
			ports["Control%s"%i] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]

		return ports

	def connectionSlots(self):
		super(TwistSystemGuide, self).connectionSlots()

		slots = {}

		start_usage = "Ctl" if self._settings["startController"] else "Bfr"
		slots["Start"] = (start_usage, "Start")
		
		usage = "Ctl" if self._settings["interControllers"] else "Bfr"
		for i in xrange(1, self.count("Part")-1):
			slots["Part%s"%i] = (usage, "Part%s"%i)
				
		end_usage = "Ctl" if self._settings["endController"] else "Bfr"
		slots["End"] = (end_usage, "End")

		if self._settings["tangent"] and self._settings["untwistDeformers"]:
			slots["UntwistStart"] = ("Rig", "UntwistStart")
		
		# Divisions
		if self._settings["startDeformer"]:
			if self._settings["tangent"]: 
				slots["Start"] = (start_usage, "Start")
			else:
				slots["Div0"] = ("Div0")
				if self._settings["untwistDeformers"]:
					slots["Untwist0"] = ("Rig", "Untwist0")
		
		for i in xrange(1, self._settings["interDeformers"]+1):
			slots["Div%s"%i] = ("Rig", "Div%s"%i)
			if self._settings["untwistDeformers"]:
				slots["Untwist%s"%i] = ("Rig", "Untwist%s"%i)
			
		if self._settings["endDeformer"]:
			if self._settings["tangent"]: 
				slots["End"] = (end_usage, "End")
			else:
				slots["Div%s"%(self._settings["interDeformers"]+1)] = ("Rig", "Div%s"%(self._settings["interDeformers"]+1))
				if self._settings["untwistDeformers"]:
					slots["Untwist%s"%i(self._settings["interDeformers"]+1)] = ("Rig", "Untwist%s"%(self._settings["interDeformers"]+1))

		if self._settings["tangent"] and self._settings["untwistDeformers"]:
			slots["UntwistEnd"] = ("Rig", "UntwistEnd")
			

		return slots

		