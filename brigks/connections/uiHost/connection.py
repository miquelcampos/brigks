from maya import cmds
from brigks.connections.systemConnection import SystemConnection

class UiHostSystemConnection(SystemConnection):

	def __init__(self):
		super(UiHostSystemConnection, self).__init__()
		self._settings = dict(
			key=None,
			slot=None,
			)

	def connect(self):
		parent = self.getParent(self._connection.settings)
		return

	def getTargetSystems(self):
		if self._settings["key"]:
			return [self._settings["key"]]
		return []

	def splitSymmetry(self, location):
		key = self._settings["key"]

		otherName, otherLocation = key.split("_")
		if otherLocation == "X":
			self._settings["key"] = "{n}_{l}".format(n=otherName, l=location)

	@staticmethod
	def getParent(settings):
		key = settings["key"]
		slot = settings["slot"]
		system = self._builder.coreBuilder.systems[key]
		parent = system.getObjectFromSlot(slot)
		return parent