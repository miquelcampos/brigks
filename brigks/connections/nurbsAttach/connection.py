from maya import cmds
import dcc.maya.dag.shape.nurbsSurface
from brigks.connections.systemConnection import SystemConnection


class NurbsAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(NurbsAttachSystemConnection, self).__init__()
		self._settings = dict(
			mesh=None,
			u=.5,
			v=.5,
			useClosest=True,
			useOrientation=True,
			key=None,
			slot=None
			)

	def connect(self, child):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		parent = self.getParent(self._connection.settings)
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

	@staticmethod
	def getParent(self, settings):
		name = "NurbsAttach"
		mesh = settings["mesh"]
		useClosest = settings["useClosest"]
		useOrientation = settings["useOrientation"]
		if useClosest:
			u, v = self._getClosestUV(mesh, position, globalSpace=True)
		else:
			u = settings["u"]
			v = settings["v"]
		key = settings["key"]
		slot = settings["slot"]

		system = self._builder.coreBuilder.systems[key]
		parent = system.getObjectFromSlot(slot)
		if not parent:
			parent = self._builder.coreBuilder.localCtl

		attach = cmds.createNode("transform", name="Attach")
		cmds.parent(parent, attach)

		#dcc.maya.compound.create("MeshMultiAttach", name, attach, mesh, componentType, componentIndex, useOrientation)
		return attach


	def _getClosestUV(self, surface, point, globalSpace=True):
		'''Returns the Closest UV values on a NurbsSurface to 'point'

		Args:
			surface(MDagPath): dagPath to the nurbsSurface shapeNode
			point(MPoint): get the closest UV to this point
			globalSpace(bool): globalSpace?
		Returns:
			(list): float UV values
		'''
		if globalSpace:
			space = om.MSpace.kWorld
		else:
			space = om.MSpace.kObject

		fnSurface = om.MFnNurbsSurface(surface)

		utilA = om.MScriptUtil()
		utilB = om.MScriptUtil()

		closestPointU = utilA.asFloatPtr()
		closestPointV = utilB.asFloatPtr()

		fnSurface.closestPoint(point, closestPointU, closestPointV, False, 0.0001, space)

		return [closestPointU.getFloat(), closestPointV.getFloat()]