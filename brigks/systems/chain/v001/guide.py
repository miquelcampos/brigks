
from brigks.systems.systemGuide import SystemGuide


class ChainSystemGuide(SystemGuide):

	markerNames = ("Bone",)
	markerMinMax = dict(
		Bone=(2,-1)
		)
	markerCompatibility = dict(
		basic=dict(Bone="Part")
		)

	def addSettings(self):
		self._settings["orientation"] = "Auto"  # Auto, Guide

		self._settings["kinematic"] = "FK"  # FK, IK or FK/IK
		self._settings["blend"] = "FK"

		self._settings["setNeutralPose"] = True
		self._settings["defaultRotationOrder"] = "XYZ"

		self._settings["strap"] = False
		self._settings["strapDeformers"] = 5

		self._settings["dynamic"] = False
		self._settings["dynActive"] = False
		self._settings["amplitude"] = 1.0

		self._settings["amplitudeX"] = 1.0
		self._settings["amplitudeY"] = 1.0
		self._settings["amplitudeZ"] = 1.0
		self._settings["decay"] = 8.0
		self._settings["frequency"] = .25
		self._settings["termination"] = 0.0

		self._settings["dynamicAnimatable"] = False

	def connectionPorts(self):
		super(ChainSystemGuide, self).connectionPorts()

		ports = dict(
			Root=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			FkRef=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			IK=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UpVector=["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"],
			UI=["uiHost"],
			)

		return ports

	def connectionSlots(self):
		super(ChainSystemGuide, self).connectionSlots()

		if self._settings["dynamic"]:
			usage = "Rig"
			name = "Dynamic{}"
		elif self._settings["kinematic"] == "FK/IK":
			usage = "Rig"
			name = "Bone{}"
		elif self._settings["kinematic"] == "FK":
			usage = "Ctrl"
			name = "Fk{}"
		else:
			usage = "Rig"
			name = "Ik{02d}"

		slots = dict()
		for i in xrange(1, self.count("Bone")):
			slots["Bone{}".format(i)] = (usage, name.format(i))

		return slots