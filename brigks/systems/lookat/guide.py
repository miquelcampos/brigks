
from brigks.systems.systemGuide import SystemGuide


class LookatSystemGuide(SystemGuide):

	markerNames = ("Part1", "Part2")
	markerMinMax = {}

	def addSettings(self):
		self.settings["addLocalController"] = True
		self.settings["addTargetController"] = True
		self.settings["addUpVController"] = False
		self.settings["extraOffsetController"] = False
		self.settings["keepRotationOffset"] = False

	def connectionPorts(self):
		super(LookatSystemGuide, self).connectionPorts()

		ports = dict(
			Root=("parent", "attachToGeo", "multi", "customParent"),
			Target=("parent", "attachToGeo", "multi", "customParent"),
			UpVector=("parent", "attachToGeo", "multi", "customParent"),
			UI=("parent", "attachToGeo", "multi", "customParent")
			)

		return ports

	def connectionSlots(self):
		super(LookatSystemGuide, self).connectionSlots()

		slots = dict(
			Direction=("Rig", "Direction"),
			Local=("Rig", "Local")
		)

		if self.settings["extraOffsetController"]:
			slots["Offset"] = ("Rig", "Offset")

		return slots
