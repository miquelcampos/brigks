from brigks.connections.systemConnection import SystemConnection
from brigks.connections.customParent.connection import CustomParentSystemConnection
from brigks.connections.meshAttach.connection import MeshAttachSystemConnection
from brigks.connections.nurbsAttach.connection import NurbsAttachSystemConnection
from brigks.connections.slotParent.connection import SlotParentSystemConnection


class MultiParentSystemConnection(SystemConnection):

	def __init__(self):
		super(MultiParentSystemConnection, self).__init__()
		self.settings = dict(definitions=[], default=0)

	def connect(self, builder, slot):
		child = builder.getObject("Ctl", slot)

		parent = None
		masters = []
		for definition in self.settings["definitions"]:
			cnxType = definition["type"]

			if cnxType == "slot":
				master = SlotParentSystemConnection.getParent(builder, definition)
				if parent is None:
					parent = master
			elif cnxType == "custom":
				master = CustomParentSystemConnection.getParent(builder, definition)
			elif cnxType == "mesh":
				master = MeshAttachSystemConnection.getParent(builder, definition)
			elif cnxType == "nurbs":
				master = NurbsAttachSystemConnection.getParent(builder, definition)

			if master:
				masters.append(master)

		if not masters:
			return

		self._parent(child, parent)
		if len(masters) == 1 and masters[0] == parent:
			return

		self._parentConstraint(child, masters)

	def getTargetSystems(self):
		keys = []
		for definition in self.settings["definitions"]:
			if "key" in definition["key"]:
				keys.append(definition["key"])
		return keys

	def splitSymmetry(self, location):
		definitions = []
		for definition in self.settings["definitions"]:
			if "key" in definition["key"]:
				key = definition["key"]

				part, otherLocation = key.split("_")
				if otherLocation != "X":
					continue

				definition["key"] = "{part}_{location}".format(part=part, location=location)

			definitions.append(definition)
		self.settings["definitions"] = definitions
