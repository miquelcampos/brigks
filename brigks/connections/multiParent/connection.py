from tools.marbie.connections.systemConnection import SystemConnection
from tools.marbie.connections.custom.connection import CustomSystemConnection
from tools.marbie.connections.mesh.connection import MeshSystemConnection
from tools.marbie.connections.nurbs.connection import NurbsSystemConnection
from tools.marbie.connections.slot.connection import SlotSystemConnection


class MultiParentSystemConnection(SystemConnection):

	def __init__(self):
		super(MultiParentSystemConnection, self).__init__()
		self.settings = dict(definitions=[])

	def connect(self, builder, slot):
		child = builder.getObject("Ctl", slot)

		parent = None
		masters = []
		for definition in self.settings["definitions"]:
			cnxType = definition["type"]

			if cnxType == "slot":
				master = SlotSystemConnection.getParent(builder, definition)
				if parent is None:
					parent = master
			elif cnxType == "custom":
				master = CustomSystemConnection.getParent(builder, definition)
			elif cnxType == "mesh":
				master = MeshSystemConnection.getParent(builder, definition)
			elif cnxType == "nurbs":
				master = NurbsSystemConnection.getParent(builder, definition)

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
