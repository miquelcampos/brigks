from maya import cmds
from brigks.connections.systemConnection import SystemConnection

class SlotParentSystemConnection(SystemConnection):

	def __init__(self):
		super(SlotParentSystemConnection, self).__init__()
		self._settings = dict(
			key=None,
			slot=None,
			)

	def connect(self, child):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		parent = self.getParent()
		self._parent(child, parent)

	def getTargetSystems(self):
		if self._settings["key"]:
			return [self._settings["key"]]
		return []

	def splitSymmetry(self, location):
		key = self._settings["key"]

		otherName, otherLocation = key.split("_")
		if otherLocation == "X":
			self._settings["key"] = "{n}_{l}".format(n=otherName, l=location)

	def getParent(self):
		system = self._builder.coreBuilder.systems[self._settings["key"]]
		return system.getObjectFromSlot(self._settings["slot"])