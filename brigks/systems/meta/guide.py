

from brigks.systems.systemGuide import SystemGuide


class MetaSystemGuide(SystemGuide):

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(2,-1)
		)

	def addSettings(self):
		pass

	def connectionPorts(self):
		super(MetaSystemGuide, self).connectionPorts()

		ports = dict(
			Root=("parent",)
			)

		return ports

	def connectionSlots(self):
		super(MetaSystemGuide, self).connectionSlots()

		slots = dict()
		for i in range(1, self.count("Part")+1):
			slots["Bone{}".format(i)] = ("Ctl", "Part{}".format(i))

		return slots
