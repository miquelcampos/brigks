
from brigks.systems.systemGuide import SystemGuide


class TwistSystemGuide(SystemGuide):	

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(2,-1)
		)

	def addSettings(self):
		self.settings["axis"] = "X" # (X, Y)
		
		self.settings["startDeformer"] = False
		self.settings["interDeformers"] = 3
		self.settings["endDeformer"] = False
		self.settings["untwistDeformers"] = False
		
		self.settings["startController"] = False
		self.settings["interControllers"] = True
		self.settings["endController"] = False
		
		self.settings["scaleWithCurve"] = False
		self.settings["scaleWithControllers"] = False
		self.settings["scaleWithInterControllers"] = False
		
		self.settings["parametric"] = True
		self.settings["preserveLength"] = False
		self.settings["tangent"] = True
		self.settings["tangentDistance"] = .25 
		self.settings["pushCurvePoints"] = False 

	def connectionPorts(self):
		super(TwistSystemGuide, self).connectionPorts()
		
		ports = {}
		for i in xrange(1, self.count("Part")+1):
			ports["Control%s"%i] = ("parent",)

		return ports

	def connectionSlots(self):
		super(TwistSystemGuide, self).connectionSlots()

		slots = {}

		start_usage = "Ctl" if self.settings["startController"] else "Bfr"
		slots["Start"] = (start_usage, "Start")
		
		usage = "Ctl" if self.settings["interControllers"] else "Bfr"
		for i in xrange(1, self.count("Part")-1):
			slots["Part%s"%i] = (usage, "Part%s"%i)
				
		end_usage = "Ctl" if self.settings["endController"] else "Bfr"
		slots["End"] = (end_usage, "End")

		if self.settings["tangent"] and self.settings["untwistDeformers"]:
			slots["UntwistStart"] = ("Rig", "UntwistStart")
		
		# Divisions
		if self.settings["startDeformer"]:
			if self.settings["tangent"]: 
				slots["Start"] = (start_usage, "Start")
			else:
				slots["Div0"] = ("Div0")
				if self.settings["untwistDeformers"]:
					slots["Untwist0"] = ("Rig", "Untwist0")
		
		for i in xrange(1, self.settings["interDeformers"]+1):
			slots["Div%s"%i] = ("Rig", "Div%s"%i)
			if self.settings["untwistDeformers"]:
				slots["Untwist%s"%i] = ("Rig", "Untwist%s"%i)
			
		if self.settings["endDeformer"]:
			if self.settings["tangent"]: 
				slots["End"] = (end_usage, "End")
			else:
				slots["Div%s"%(self.settings["interDeformers"]+1)] = ("Rig", "Div%s"%(self.settings["interDeformers"]+1))
				if self.settings["untwistDeformers"]:
					slots["Untwist%s"%i(self.settings["interDeformers"]+1)] = ("Rig", "Untwist%s"%(self.settings["interDeformers"]+1))

		if self.settings["tangent"] and self.settings["untwistDeformers"]:
			slots["UntwistEnd"] = ("Rig", "UntwistEnd")
			

		return slots

		