from maya import cmds
import dcc.maya.dag.shape.nurbsSurface
from brigks.connections.systemConnection import SystemConnection


class NurbsAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(NurbsAttachSystemConnection, self).__init__()
		self.settings = dict(
			mesh=None,
			u=.5,
			v=.5,
			useClosest=True,
			useOrientation=True,
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
		name = "NurbsAttach"
		mesh = settings["mesh"]
		useClosest = settings["useClosest"]
		useOrientation = settings["useOrientation"]
		if useClosest:
			u, v = dcc.maya.dag.shape.nurbsSurface.getClosestUV(mesh, position, globalSpace=True)
		else:
			u = settings["u"]
			v = settings["v"]
		key = settings["key"]
		slot = settings["slot"]

		system = builder.coreBuilder.systems[key]
		parent = system.getObjectFromSlot(slot)
		if not parent:
			parent = builder.coreBuilder.localCtl

		attach = cmds.createNode("transform", name="Attach")
		cmds.parent(parent, attach)

		#dcc.maya.compound.create("MeshMultiAttach", name, attach, mesh, componentType, componentIndex, useOrientation)
		return attach
