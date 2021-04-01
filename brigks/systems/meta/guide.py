

from tools.marbie.systems.systemGuide import SystemGuide


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
		for i in range(self.count("Part"), start=1):
			slots["Bone{}".format(i)] = ("Ctl", "Part{}".format(i))

		return slots
