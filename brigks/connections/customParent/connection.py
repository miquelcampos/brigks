from maya import cmds
from brigks.connections.systemConnection import SystemConnection


class CustomParentSystemConnection(SystemConnection):

	def __init__(self):
		super(CustomParentSystemConnection, self).__init__()
		self.settings = dict(parent=None)

	def connect(self, builder, slot):
		child = builder.getObject("Ctl", slot)
		parent = self.getParent(builder, self._connection.settings)
		self._parent(child, parent)

	@staticmethod
	def getParent(builder, settings):
		model = builder.coreBuilder.model
		parent = settings["parent"]
		for parent in [cmds.ls(parent, long=True)]:
			if parent.startswith(model):
				return parent