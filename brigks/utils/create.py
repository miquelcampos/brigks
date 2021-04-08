from maya import cmds

from math3d.transformation import TransformationArray
from math3d.vectorN import Vector3

from brigks.utils import attr

ICONS = ["arrow", "bone", "circle", "compass", "cross", "crossarrow", "cube", "cubewithpeak",
	"cylinder", "diamond", "flower", "jaw", "null", "pyramid", "sphere", "spine", "square",
	 "lookat", "bendedarrow", "rotatearrow", "gear", "lung"]

def transform(parent, name, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
	node = cmds.createNode("transform", name=name)
	attr.setColor(node, color)
	cmds.parent(node, parent)

	# Transform
	cmds.xform(node, matrix=tfm.asMatrix().flattened(), worldSpace=True)

	return node

def joint(parent, name, tfm=None, color=None):
	node = cmds.createNode("joint", name=name)
	attr.setColor(node, color)
	cmds.parent(node, parent)

	# Transform
	if tfm is None:
		# If no Transform is passed, we match the parent position
		matrix = cmds.xform(parent, q=True, matrix=True, worldSpace=True)
	else:
		matrix = tfm.asMatrix().flattened()
	cmds.xform(node, matrix=matrix, worldSpace=True)
	
	return node

def icon(icon, parent=None, size=1, po=None, ro=None, so=None, showCenter=False, showOrientation=False, centerScale=1.0):
	if not cmds.pluginInfo("harbieLocator.mll", q=True, loaded=True): 
		cmds.loadPlugin("harbieLocator.mll")

	shape = cmds.createNode("nurbsCurve", name=parent+"Shape", parent=parent, skipSelect=True)
	mhc =  cmds.createNode("makeHarbieCurve", skipSelect=True)
	cmds.connectAttr (mhc+".outputCurve", shape+".create")

	# Icon
	cmds.setAttr(mhc+".display", ICONS.index(icon.lower()))
	cmds.setAttr(mhc+".size", size)

	# Icon Offset Transform
	if po:
		for value, s in zip(po, "XYZ"):
			cmds.setAttr(mhc+".localPosition%s"%s, value)
	if ro:
		for value, s in zip(ro, "XYZ"):
			cmds.setAttr(mhc+".localRotate%s"%s, value)
	if so:
		for value, s in zip(so, "XYZ"):
			cmds.setAttr(mhc+".localScale%s"%s, value)

	cmds.setAttr(mhc+".ShowCenter", showCenter)
	cmds.setAttr(mhc+".ShowOrientation", showOrientation)
	cmds.setAttr(mhc+".CenterScale", centerScale)

# ----------------------------------------------------------------------------------
#  CHAIN
# ----------------------------------------------------------------------------------
def chain(name, parent, positions, normal=None, axis="xz", negate=False, size=1, color=None):
	if normal is None:
		if len(positions) >= 3:
			normal = Vector3.planeNormal(positions, normalize=True)
		else:
			normal = Vector(0,0,-1)

	# Transform.setMirrorMethod(Transform.inversedRotation)
	transforms = TransformationArray.chain(positions, normal, axis, negate, endTransform=True)
	d = [(positions[i],positions[i+1]) for i in range(len(positions)-1)]
	lengths = [Vector3.distance(a,b) for a,b in d] + [1]

	joints = []
	jointParent = parent
	for i, tfm in enumerate(transforms, start=1):
		# joint = create(name+"%02d"%i, jointParent, tfm, size, color)
		jnt = joint(jointParent, name+"%02d"%i, tfm, color)

		jointParent = jnt
		joints.append(jnt)

	handle, effector = cmds.ikHandle(startJoint=joints[0], endEffector=joints[-1])

	if negate:
		upv = Vector3(0,-1,0) * transforms[0]
		tfm = transforms[0].copy(rotation=Euler(0,0,0))
		upv = upv * tfm.inverted()

		cmds.setAttr(handle+".poleVectorX", upv.x)
		cmds.setAttr(handle+".poleVectorY", upv.y)
		cmds.setAttr(handle+".poleVectorZ", upv.z)

	effector = cmds.rename(effector, name+"Eff")
	handle = cmds.rename(handle, name+"Hdl")
	if parent:
		cmds.parent(handle, parent, absolute=True)

	cmds.delete(joints.pop(-1))

	return joints, effector, handle
