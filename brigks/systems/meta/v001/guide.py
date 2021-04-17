from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class MetaSystemGuide(SystemGuide):

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(2,-1)
		)
	markerPositions = dict(
		Part1=Vector3([55,105,15]),
		Part2=Vector3([55,105,13]),
		Part3=Vector3([55,105,11]),
		Part4=Vector3([55,105,9]),
		)

	def addSettings(self):
		pass

	def connectionPorts(self):
		super(MetaSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]
			)

		return ports

	def connectionSlots(self):
		super(MetaSystemGuide, self).connectionSlots()

		slots = dict()
		for i in range(1, self.count("Part")+1):
			slots["Bone{}".format(i)] = ("Ctl", "Part{}".format(i))

		return slots
