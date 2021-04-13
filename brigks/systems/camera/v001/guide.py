

from brigks.systems.systemGuide import SystemGuide


class CameraSystemGuide(SystemGuide):

	markerNames = ("Root",)
	markerMinMax = {}

	def addSettings(self):
		pass

	def connectionPorts(self):
		super(CameraSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["uiHost"]
			)

		return ports

	def connectionSlots(self):
		super(CameraSystemGuide, self).connectionSlots()