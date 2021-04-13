from maya import cmds

from brigks.systems.systemGuide import SystemGuide

class FootSystemGuide(SystemGuide):	

	markerNames = ("Part", "Heel", "In", "Out")
	markerMinMax = dict(
		Part=(1,-1)
		)

	def addSettings(self):
		for i in range(self.count("Part")):
			self._settings["angle%s"%(i+1)] = 20
			
		self._settings["rollControl"] = "Slider" # Slider, Controller

	def connectionPorts(self):
		super(FootSystemGuide, self).connectionPorts()
		
		ports = dict(
			Root=["legAttach"],
			UI=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(FootSystemGuide, self).connectionSlots()

		slots = dict(
			Root=("Rig", "FkRef")
			)

		for i in xrange(1, self.count("Part")):
			slots["Bone%s"%i] = ("Ctl", "Fk%s"%i)

		return slots

		