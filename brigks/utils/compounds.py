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
