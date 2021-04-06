from maya import cmds
from maya import OpenMaya as om

from brigks.connections.systemConnection import SystemConnection

COMPONENT_TYPES = ["vertex", "edge", "face"]

class MeshAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(MeshAttachSystemConnection, self).__init__()
		self._settings = dict(
			mesh=None,
			componentType="vertex",
			componentIndex=-1,
			useClosest=True,
			useOrientation=False,
			key=None,
			slot=None
			)

	def connect(self, child):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		translation = cmds.xform(child, q=True, translation=True, worldSpace=True)
		parent = self.getParent(self._settings, translation)
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

	def getParent(self, settings, translation):
		mesh = settings["mesh"]
		useClosest = settings["useClosest"]
		useOrientation = settings["useOrientation"]
		componentType = COMPONENT_TYPES.index(settings["componentType"])
		componentIndex = -1 if useClosest else settings["componentIndex"]
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
		cmds.xform(attach, translation=translation, worldSpace=True)

		self._meshMultiAttach(attach, mesh, componentType, componentIndex, useOrientation)
		return attach

	#----------------------------------------------------------------------------
	#  
	#----------------------------------------------------------------------------
	def _meshMultiAttach(self, slave, mesh, attach=0, index=-1, orient=False):
		'''
		Args:
			slave(): 
			mesh(): 
			attach(int): 0 Vertex, 1 Edge, 2 Polygon
			index(int): -1 to auto detect closest index
			orient(bool): True to compute orientation from component normal/tangent (slower)
		'''
		if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
			cmds.loadPlugin("HarbieNodes")

		shape = cmds.listRelatives(mesh, shapes=True, path=True)[0]

		if index == -1:
			pos = cmds.xform(slave, q=True, translation=True, worldSpace=True)
			index = self._closestComponentIndex(shape, pos, attach)

		# We're not creating a new node if there is already one available using the correct attach method
		mmaNode = self._getExistingNode(shape, attach)
		attrIndex = self._getNextAvailableIndex(mmaNode)

		cmds.connectAttr(shape+".outMesh", mmaNode+".mesh", force=True)
		cmds.connectAttr(mesh+".worldMatrix[0]", mmaNode+".meshMatrix", force=True)
		cmds.setAttr(mmaNode+".attach", attach)

		cmds.connectAttr(slave+".parentInverseMatrix[0]", mmaNode+".component[%s].parentInverse"%attrIndex)
		cmds.setAttr(mmaNode+".component[%s].index"%attrIndex, index)
		cmds.setAttr(mmaNode+".component[%s].orient"%attrIndex, orient)

		cmds.connectAttr(mmaNode+".output[%s].translate"%attrIndex, slave+".translate")
		if orient:
			cmds.connectAttr(mmaNode+".output[%s].rotate"%attrIndex, slave+".rotate")

	def _getExistingNode(self, shape, attach):
		nodes = cmds.listConnections(shape, type="MeshMultiAttach")
		if nodes:
			for node in nodes:
				if cmds.getAttr(node+".attach") == attach:
					return node

		return cmds.createNode("MeshMultiAttach", name="MshMAttch")

	def _getNextAvailableIndex(self, node):
		indices = cmds.getAttr(node+".component", mi=True)
		if indices:
			return max(indices) + 1
		else:
			return 0

	def _closestComponentIndex(self, shape, position, componentType):
		'''	Get the closest component Index to given position

		Args:
			mesh
			position(MPoint|MVector) : 
			componentType(int) : 0 Vertex, 1 Edge, 2 Polygon

		Return:
			int
		'''
		point = om.MPoint(*position)
		shape = self._getMFnMesh(shape)

		util = om.MScriptUtil()
		util.createFromInt(0)
		idPointer = util.asIntPtr()

		shape.getClosestPoint(point, om.MPoint(), om.MSpace.kObject, idPointer)
		faceId = om.MScriptUtil(idPointer).asInt()
		if componentType == 2: #Face
			return faceId

		elif componentType == 1: # Edge
			faceIter = om.MItMeshPolygon(shape.object())
			faceIter.setIndex(faceId, idPointer)
			array = om.MIntArray()
			faceIter.getEdges(array)

			edgeIter = om.MItMeshEdge(shape.object())

			length = 99999999999.999
			edgeId = None
			for i, currentEdgeId in enumerate(array):
				edgeIter.setIndex(currentEdgeId, idPointer)
				edgePoint = edgeIter.center(om.MSpace.kObject)
				currentLenght = point.distanceTo(edgePoint)
				if currentLenght < length:
					length = currentLenght
					edgeId = currentEdgeId
			return edgeId

		elif componentType == 0: # Vertex
			faceIter = om.MItMeshPolygon(shape.object())
			faceIter.setIndex(faceId, idPointer)
			array = om.MIntArray()
			faceIter.getVertices(array)
			length = 99999999999.999
			vertexId = None
			for i, currentVertexId in enumerate(array):
				vertexPoint = om.MPoint()
				shape.getPoint(currentVertexId, vertexPoint, om.MSpace.kObject)
				currentLenght = point.distanceTo(vertexPoint)
				if currentLenght < length:
					length = currentLenght
					vertexId = currentVertexId
			return vertexId

	def _getMFnMesh(self, shapePath):
		mobj = om.MObject()
		selectionList = om.MSelectionList()
		selectionList.add(str(shapePath))
		selectionList.getDependNode(0,mobj)
		return om.MFnMesh(mobj)


