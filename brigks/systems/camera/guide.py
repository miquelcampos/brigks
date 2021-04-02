

from brigks.systems.systemGuide import SystemGuide


class CameraSystemGuide(SystemGuide):

	markerNames = ("Part1",)
	markerMinMax = {}

	def addSettings(self):
		pass

	def connectionPorts(self):
		super(CameraSystemGuide, self).connectionPorts()

		ports = dict(
			Root=("parent",)
			)

		return ports

	def connectionSlots(self):
		super(CameraSystemGuide, self).connectionSlots()