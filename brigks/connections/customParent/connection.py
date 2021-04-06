from maya import cmds
from brigks.connections.systemConnection import SystemConnection


class CustomParentSystemConnection(SystemConnection):

	def __init__(self):
		super(CustomParentSystemConnection, self).__init__()
		self._settings = dict(parent=None)

	def connect(self, child):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		parent = self.getParent(self._builder, self._connection.settings)
		self._parent(child, parent)

	@staticmethod
	def getParent(settings):
		model = self._builder.coreBuilder.model
		parent = settings["parent"]
		for parent in [cmds.ls(parent, long=True)]:
			if parent.startswith(model):
				return parent