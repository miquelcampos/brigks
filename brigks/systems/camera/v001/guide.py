
from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide

class CameraSystemGuide(SystemGuide):

	markerNames = ("Root",)
	markerPositions = dict(
		Root=Vector3([0,175,60]),
		)

	def addSettings(self):
		pass

	def connectionPorts(self):
		super(CameraSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "multiParent", "customParent"],
			)

		return ports

	def connectionSlots(self):
		super(CameraSystemGuide, self).connectionSlots()