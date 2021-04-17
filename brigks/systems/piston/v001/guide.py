from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class PistonSystemGuide(SystemGuide):	

	markerNames = ("Root", "Eff")
	markerPositions = dict(
		Root=Vector3([10,0,0]),
		Eff=Vector3([10,10,0]),
		)

	def addSettings(self):
		self._settings["addControllers"] = False
		self._settings["interDeformers"] = 0

	def connectionPorts(self):
		super(PistonSystemGuide, self).connectionPorts()
		
		ports = dict(
			Start=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			End=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(PistonSystemGuide, self).connectionSlots()

		slots = dict(
			StretchStart=("Rig", "StretchStart"),
			StretchEnd=("Rig", "StretchEnd")
			)
		for i in xrange(1, self.settings("interDeformers")+1):
			slots["Div{}".format(i)] = ("Rig", "Div{}".format(i))

		return slots
