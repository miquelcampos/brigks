from itertools import izip

from maya import cmds

from math3d.matrixN import Matrix4

compareOps = ["==", "!=", ">", ">=", "<", "<="]
def compare(first, second, operation):
	if operation not in compareOps:
		raise ValueError("Given operation must be in %s"%compareOps)

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

	cmds.setAttr(node+".operation", compareOps.index(operation))

	cmds.setAttr(node+".colorIfTrueR", 1)
	cmds.setAttr(node+".colorIfFalseR", 0)

	return node


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



