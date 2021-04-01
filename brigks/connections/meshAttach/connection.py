from maya import cmds
import dcc.maya.compound
from tools.marbie.connections.systemConnection import SystemConnection


class MeshAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(MeshAttachSystemConnection, self).__init__()
		self.settings = dict(
			mesh=None,
			componentType="vertex",
			componentIndex=-1,
			useClosest=True,
			useOrientation=False,
			key=None,
			slot=None
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
		name = "MultiAttach"
		mesh = settings["mesh"]
		useClosest = settings["useClosest"]
		useOrientation = settings["useOrientation"]
		componentType = settings["componentType"]
		componentIndex = -1 if useClosest else settings["componentIndex"]
		key = settings["key"]
		slot = settings["slot"]

		system = builder.coreBuilder.systems[key]
		parent = system.getObjectFromSlot(slot)
		if not parent:
			parent = builder.coreBuilder.localCtl

		attach = cmds.createNode("transform", name="Attach")
		cmds.parent(parent, attach)

		dcc.maya.compound.create("MeshMultiAttach", name, attach, mesh, componentType, componentIndex, useOrientation)
		return attach