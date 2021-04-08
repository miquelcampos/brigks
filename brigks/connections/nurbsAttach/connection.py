from maya import cmds
from maya import OpenMaya as om

from brigks.utils import compounds
from brigks.connections.systemConnection import SystemConnection

class NurbsAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(NurbsAttachSystemConnection, self).__init__()
		self._settings = dict(
			surface=None,
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

		position = cmds.xform(child, q=True, translation=True, worldSpace=True)
		parent = self.getParent(self._settings, position)
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

	def getParent(self, settings, position):
		surface = settings["surface"]
		useClosest = settings["useClosest"]
		useOrientation = settings["useOrientation"]
		if useClosest:
			u, v = self._getClosestUV(surface, position, globalSpace=True)
		else:
			u = settings["u"]
			v = settings["v"]
		key = settings["key"]
		slot = settings["slot"]

		parent = None
		if key and slot:
			system = self._builder.coreBuilder.systems[key]
			parent = system.getObjectFromSlot(slot)
		if parent is None:
			parent = self._builder.coreBuilder.localCtl

		attachName = self.getObjectName(usage="Rig", part="MeshAttach")
		attach = cmds.createNode("transform", name=attachName)
		cmds.parent(attach, parent)
		cmds.xform(attach, translation=position, worldSpace=True)

		compounds.surfaceMultiAttach([[attach]], surface, 0, [u], [v])
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

		point = om.MPoint(*point)

		#shape = cmds.listRelatives(surface, shapes=True, path=True)[0]
		fnSurface = self._getMFnNurbsSurface(surface)

		utilA = om.MScriptUtil()
		utilB = om.MScriptUtil()

		closestPointU = utilA.asDoublePtr()
		closestPointV = utilB.asDoublePtr()

		fnSurface.closestPoint(point, closestPointU, closestPointV, False, 1e-4, space)

		closestPointU = utilA.getDouble(closestPointU)
		closestPointV = utilB.getDouble(closestPointV)
		return [closestPointU, closestPointV]

	def _getMFnNurbsSurface(self, path):
		mobj = om.MObject()
		dagPath = om.MDagPath()
		selectionList = om.MSelectionList()
		selectionList.add(str(path))
		selectionList.getDependNode(0,mobj)


		selectionList.getDagPath(0, dagPath)

		return om.MFnNurbsSurface(dagPath)
