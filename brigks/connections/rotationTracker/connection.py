from maya import cmds
from tools.marbie.connections.systemConnection import SystemConnection

class RotationTrackerSystemConnection(SystemConnection):

	def __init__(self):
		super(RotationTrackerSystemConnection, self).__init__()
		self.settings = dict(
			referenceKey=None,
			referenceSlot=None,
			trackerKey=None,
			trackerSlot=None,
			)

	def connect(self, builder, slot):
		child = builder.getObject("Ctl", slot)

		referenceKey = self.settings["referenceKey"]
		referenceSlot = self.settings["referenceSlot"]
		system = builder.coreBuilder.systems[referenceKey]
		reference = system.getObjectFromSlot(referenceSlot)

		trackerKey = self.settings["trackerKey"]
		trackerSlot = self.settings["trackerSlot"]
		system = builder.coreBuilder.systems[trackerKey]
		tracker = system.getObjectFromSlot(trackerSlot)

		cns = dcc.maya.compound.create("rotationTracker", "rotTracker", outrotAttr, reference, tracker)

		return

	def getTargetSystems(self):
		keys = []
		if self.settings["referenceKey"]:
			return keys.append(self.settings["referenceKey"])
		if self.settings["trackerKey"]:
			return keys.append(self.settings["trackerKey"])
		return keys

	def splitSymmetry(self, location):
		referenceKey = self.settings["referenceKey"]
		otherName, otherLocation = referenceKey.split("_")
		if otherLocation == "X":
			self.settings["referenceKey"] = "{n}_{l}".format(n=otherName, l=location)
		trackerKey = self.settings["trackerKey"]
		otherName, otherLocation = trackerKey.split("_")
		if otherLocation == "X":
			self.settings["trackerKey"] = "{n}_{l}".format(n=otherName, l=location)

	# @staticmethod
	# def getParent(builder, settings):
	# 	key = settings["key"]
	# 	slot = settings["slot"]
	# 	system = builder.coreBuilder.systems[key]
	# 	parent = system.getObjectFromSlot(slot)
	# 	return parent