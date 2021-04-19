from math3d.vectorN import Vector3

from brigks.systems.systemGuide import SystemGuide
from brigks import config

class SpineSystemGuide(SystemGuide):

	markerNames = ("Root", "Eff")
	markerPositions = dict(
		Root=Vector3([0,100,0]),
		Eff=Vector3([0,135,0]),
		)

	def addSettings(self):
		self._settings["blend"] = "IK" # FK, IK
		self._settings["breathing"] = False
		self._settings["axis"] = "YZ"


	def connectionPorts(self):
		super(SpineSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"])

		return ports

	def connectionSlots(self):
		super(SpineSystemGuide, self).connectionSlots()

		slots = dict(
			Pelvis=(config.USE_CTL, "Ik1"),
			Lower=(config.USE_RIG, "Hook2"),
			Middle=(config.USE_RIG, "Hook3"),
			Upper=(config.USE_RIG, "Hook4"),
			Chest=(config.USE_RIG, "Hook5"),
			Breathing=(config.USE_CTL, "Breathing")
			)

		return slots
