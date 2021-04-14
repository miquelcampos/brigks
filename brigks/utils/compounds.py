from itertools import izip
import math

from maya import cmds

from math3d.matrixN import Matrix4

COMPARE_OPS = ["==", "!=", ">", ">=", "<", "<="]
def compare(first, second, operation):
	if operation not in COMPARE_OPS:
		raise ValueError("Given operation must be in %s"%COMPARE_OPS)

	node = cmds.createNode("condition", name="Cond")

	if isinstance(first, float) or isinstance(first, int):
		cmds.setAttr(node+".firstTerm", first)
	else:
		cmds.connectAttr(first, node+".firstTerm")

	if isinstance(second, float) or isinstance(second, int):
		cmds.setAttr(node+".secondTerm", second)
	else:
		second = attribute.get(*second)
		cmds.connectAttr(second, node+".secondTerm")

	cmds.setAttr(node+".operation", COMPARE_OPS.index(operation))

	cmds.setAttr(node+".colorIfTrueR", 1)
	cmds.setAttr(node+".colorIfFalseR", 0)

	return node

# ----------------------------------------------------------------------------------
# TRANSFORMS
# ----------------------------------------------------------------------------------
def blendMatrix(slave, masters, maintainOffset=False, translate=True, rotate=True, scale=True, useJointOrient=False):
	bmNode = cmds.createNode("blendMatrix", name="BlendMatrix")
	mmNode = cmds.createNode("multMatrix", name="MultMatrix")
	dmNode = cmds.createNode("decomposeMatrix", name="DecomposeMatrix")

	cmds.connectAttr(bmNode+".outputMatrix", mmNode+".matrixIn[0]")
	cmds.connectAttr(slave+".parentInverseMatrix[0]", mmNode+".matrixIn[1]")
	cmds.connectAttr(mmNode+".matrixSum", dmNode+".inputMatrix")

	# Input
	slaveMatrix = cmds.xform(slave, q=True, matrix=True, worldSpace=True)
	slaveMatrix = Matrix4(slaveMatrix)
	for i, master in enumerate(masters):
		if maintainOffset:
			masterMatrix = cmds.xform(master, q=True, matrix=True, worldSpace=True)
			masterMatrix = Matrix4(masterMatrix)
			offset = slaveMatrix * masterMatrix.inverse()

			offNode = cmds.createNode("multMatrix", name="Offset{}".format(i))
			cmds.setAttr(offNode+".matrixIn[0]", offset.flattened(), type="matrix")
			cmds.connectAttr(master+".worldMatrix[0]", offNode+".matrixIn[1]")
			cmds.connectAttr(offNode+".matrixSum", bmNode+".target[{}].targetMatrix".format(i))
		else:
			cmds.connectAttr(master+".worldMatrix[0]", bmNode+".target[{}].targetMatrix".format(i))

	# Output
	if translate:
		cmds.connectAttr(dmNode+".outputTranslate", slave+".translate", force=True)
	if rotate:
		if cmds.nodeType(slave) == "joint" and useJointOrient:
			cmds.connectAttr(dmNode+".outputRotate", slave+".jointOrient", force=True)
		else:
			cmds.connectAttr(dmNode+".outputRotate", slave+".rotate", force=True)

	if scale:
		cmds.connectAttr(dmNode+".outputScale", slave+".scale", force=True)
		cmds.connectAttr(dmNode+".outputShear", slave+".shear", force=True)

	return bmNode

def aimConstraint(name, slave, master, axis="xy", upMaster=None, upVector=None):
	# TODO Replace with aimMatrix
	cns = cmds.aimConstraint(master, slave, worldUpType="objectrotation", maintainOffset=False, name=name, skip="none")[0]

	# UpVector
	cmds.setAttr(cns+".worldUpVectorX", upVector[0])
	cmds.setAttr(cns+".worldUpVectorY", upVector[1])
	cmds.setAttr(cns+".worldUpVectorZ", upVector[2])

	cmds.connectAttr(upMaster+".worldMatrix[0]", cns+".worldUpMatrix")

	# Direction Axis
	aimAttr = ["aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ"]
	a = axis.replace("-", "")
	out = [0]*6
	out["xyz".index(a[0])] = -1 if axis[0] == "-" else 1
	out["xyz".index(a[1])+3] = -1 if axis[-2] == "-" else 1
	for name, value in izip(aimAttr, out):
		cmds.setAttr(cns+"."+name, value)

	return cns

POINTAT_AXIS = ["X", "Y", "Z", "-X", "-Y", "-Z"]
def pointAtBlendedAxis(cns, masterA, masterB, blend=.5, axis="Z"):
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")
	node = cmds.createNode("PointAtBlendedAxis", name="PtAtBlended")
	cmds.connectAttr(masterA+".worldMatrix[0]", node+".mA")
	cmds.connectAttr(masterB+".worldMatrix[0]", node+".mB")

	cmds.setAttr(node+".axis", POINTAT_AXIS.index(axis))
	cmds.setAttr(node+".blend", blend)

	cmds.setAttr(cns+".worldUpType", 3)
	cmds.connectAttr(node+".out", cns+".worldUpVector")

	return node

def harmonic(name, slave, master, amplitude=1.0, decay=8.0, frequency=0.5, termination=0.0, amplitudeAxis=(1,1,1)):
	if not cmds.pluginInfo("harmonics", q=True,  loaded=True):
		cmds.loadPlugin("harmonics")
	hNode = cmds.createNode("harmonics", name=name)

	cmds.connectAttr(hNode+".output", slave+".translate")
	cmds.connectAttr(master+".wm", hNode+".input")
	cmds.connectAttr(master+".pim", hNode+".parentInverse")
	cmds.connectAttr("time1.o", hNode+".timeIn")

	cmds.setAttr(hNode+".update", True)
	cmds.setAttr(hNode+".amplitude", amplitude)
	cmds.setAttr(hNode+".axisAmp0", amplitudeAxis[0])
	cmds.setAttr(hNode+".axisAmp1", amplitudeAxis[1])
	cmds.setAttr(hNode+".axisAmp2", amplitudeAxis[2])
	cmds.setAttr(hNode+".decay", decay)
	cmds.setAttr(hNode+".frequencyMult", frequency)
	cmds.setAttr(hNode+".termination", termination)

	return hNode

def rotationTracker(attr, reference, tracker):
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	node = cmds.createNode("RotationTracker", name="RotTrk")

	cmds.connectAttr(reference+".worldMatrix[0]", node+".reference")
	cmds.connectAttr(tracker+".worldMatrix[0]", node+".tracker")

	# Offset
	tMatrix = Matrix4(cmds.xform(tracker, q=True, matrix=True, worldSpace=True))
	rMatrix = Matrix4(cmds.xform(tracker, q=True, matrix=True, worldSpace=True))
	m = tMatrix * rMatrix.inverse()
	er = tMatrix.asTransform().rotation.asEuler()
	x = math.degrees(er.x)
	y = math.degrees(er.y)
	z = math.degrees(er.z)
	cmds.setAttr(node+".restX", x)
	cmds.setAttr(node+".restY", y)
	cmds.setAttr(node+".restZ", z)

	cmds.connectAttr(node+".output", attr, force=True)

	return node

def rotationToSlider(attr, rotMin=-90, rotMax=90, slideMin=0, slideMax=1):
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	node = cmds.createNode("RotationToSlider", name="RTS")

	cmds.connectAttr(node+".output", attr)
	cmds.setAttr(node+".rotMin", rotMin)
	cmds.setAttr(node+".rotMax", rotMax)
	cmds.setAttr(node+".sliderMin", slideMin)
	cmds.setAttr(node+".sliderMax", slideMax)

	return node

# ----------------------------------------------------------------------------------
# ATTACH
# ----------------------------------------------------------------------------------
def surfaceAttach(slave, surface, u=None, v=None):
	if u is None or v is None:
		u, v = self._getClosestUV(surface, position, globalSpace=True)

	compounds.surfaceMultiAttach([[slave]], surface, 0, [u], [v])
	return attach

def surfaceMultiAttach(slaves, surface, attach=0, uParams=None, vParams=None, evenly=False):
	'''
	Args:
		slaves(List of List of Transform): 
		surface(): 
		attach(int): 0 Parametric, 1 Percentage, 2 Fixed Length
		uParams(list of double|None): None for linear distribution. double must be between 0.0 and 1.0
		vParams(list of double|None): None for linear distribution. double must be between 0.0 and 1.0
	'''
	if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
		cmds.loadPlugin("HarbieNodes")

	shape = cmds.listRelatives(surface, shapes=True, path=True)[0]

	vCount = len(slaves)
	uCount = len(slaves[0])

	if uParams is not None and len(uParams) != uCount:
		raise RuntimeError("Number of uParams doesn't match u count")
	if vParams is not None and len(vParams) != vCount:
		raise RuntimeError("Number of vParams doesn't match u count")

	
	# This is a custom command part of the Harbie Plugin
	length = cmds.surfaceInfo(surface, length=True)

	cmaNode = cmds.createNode("SurfaceMultiAttach", name="SrfMAttch")

	cmds.connectAttr(shape+".local", cmaNode+".surface")
	cmds.connectAttr(surface+".worldMatrix[0]", cmaNode+".surfaceMatrix")
	cmds.connectAttr(slaves[0][0]+".parentInverseMatrix[0]", cmaNode+".parentInverse")
	cmds.setAttr(cmaNode+".attach", attach)
	cmds.setAttr(cmaNode+".length", length)

	# V
	if vParams is None:
		if vCount == 1:
			vParams = [0.5]
		else:
			vParams = [j/float(vCount-1) for j in range(vCount)]
	
	# U
	if uParams is None:
		uParams = []
		if uCount == 1:
			uParams = [0.5]
		else:
			isClosed = cmds.getAttr(shape+".formU") != 0 
			count = float(uCount) if isClosed else float(uCount-1)
			for i in range(uCount):
				step = i/count
				if attach==0 and evenly:
					# This is a custom command part of the Harbie Plugin
					uParams.append(cmds.surfaceInfo(surface, pfp=step))
				else:
					uParams.append(step)

			
	for j, v in enumerate(vParams):
		cmds.setAttr(cmaNode+".v[%s]"%j, v)
	for i, u in enumerate(uParams):
		cmds.setAttr(cmaNode+".u[%s]"%i, u)


	for j in range(vCount):
		for i in range(uCount):
			index = j*uCount+i
			slave = slaves[j][i]
			cmds.connectAttr(cmaNode+".output[%s].translate"%index, slave+".translate")
			cmds.connectAttr(cmaNode+".output[%s].rotate"%index, slave+".rotate")


def meshMultiAttach(slave, mesh, attach=0, index=-1, orient=False):
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
		index = _closestComponentIndex(shape, pos, attach)

	# We're not creating a new node if there is already one available using the correct attach method
	mmaNode = _getExistingNode(shape, attach)
	attrIndex = _getNextAvailableIndex(mmaNode)

	cmds.connectAttr(shape+".outMesh", mmaNode+".mesh", force=True)
	cmds.connectAttr(mesh+".worldMatrix[0]", mmaNode+".meshMatrix", force=True)
	cmds.setAttr(mmaNode+".attach", attach)

	cmds.connectAttr(slave+".parentInverseMatrix[0]", mmaNode+".component[%s].parentInverse"%attrIndex)
	cmds.setAttr(mmaNode+".component[%s].index"%attrIndex, index)
	cmds.setAttr(mmaNode+".component[%s].orient"%attrIndex, orient)

	cmds.connectAttr(mmaNode+".output[%s].translate"%attrIndex, slave+".translate")
	if orient:
		cmds.connectAttr(mmaNode+".output[%s].rotate"%attrIndex, slave+".rotate")

def _getExistingNode(shape, attach):
	nodes = cmds.listConnections(shape, type="MeshMultiAttach")
	if nodes:
		for node in nodes:
			if cmds.getAttr(node+".attach") == attach:
				return node

	return cmds.createNode("MeshMultiAttach", name="MshMAttch")

def _getNextAvailableIndex(node):
	indices = cmds.getAttr(node+".component", mi=True)
	if indices:
		return max(indices) + 1
	else:
		return 0

def _closestComponentIndex(shape, position, componentType):
	'''	Get the closest component Index to given position

	Args:
		mesh
		position(MPoint|MVector) : 
		componentType(int) : 0 Vertex, 1 Edge, 2 Polygon

	Return:
		int
	'''
	point = om.MPoint(*position)
	shape = _getMFnMesh(shape)

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

def _getMFnMesh(shapePath):
	mobj = om.MObject()
	selectionList = om.MSelectionList()
	selectionList.add(str(shapePath))
	selectionList.getDependNode(0,mobj)
	return om.MFnMesh(mobj)

def _getClosestUV(surface, point, globalSpace=True):
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
	fnSurface = _getMFnNurbsSurface(surface)

	utilA = om.MScriptUtil()
	utilB = om.MScriptUtil()

	closestPointU = utilA.asDoublePtr()
	closestPointV = utilB.asDoublePtr()

	fnSurface.closestPoint(point, closestPointU, closestPointV, False, 1e-4, space)

	closestPointU = utilA.getDouble(closestPointU)
	closestPointV = utilB.getDouble(closestPointV)
	return [closestPointU, closestPointV]

def _getMFnNurbsSurface(path):
	mobj = om.MObject()
	dagPath = om.MDagPath()
	selectionList = om.MSelectionList()
	selectionList.add(str(path))
	selectionList.getDependNode(0,mobj)


	selectionList.getDagPath(0, dagPath)

	return om.MFnNurbsSurface(dagPath)
