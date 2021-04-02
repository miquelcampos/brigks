from maya import cmds
from brigks.connections.systemConnection import SystemConnection

class SlotParentSystemConnection(SystemConnection):

	def __init__(self):
		super(SlotParentSystemConnection, self).__init__()
		self.settings = dict(
			key=None,
			slot=None,
			)

	def connect(self, builder, slot):
		child = builder.getObject("Ctl", slot)
		parent = self.getParent(builder, self._connection.settings)
		self._parent(child, parent)

	def getTargetSystems(self):
		if self.settings["key"]:
			return [self.settings["key"]]
		return []

	def splitSymmetry(self, location):
		key = self.settings["key"]

		otherName, otherLocation = key.split("_")
		if otherLocation == "X":
			self.settings["key"] = "{n}_{l}".format(n=otherName, l=location)

	@staticmethod
	def getParent(builder, settings):
		key = settings["key"]
		slot = settings["slot"]
		system = builder.coreBuilder.systems[key]
		parent = system.getObjectFromSlot(slot)
		return parent