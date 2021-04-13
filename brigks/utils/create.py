from maya import cmds
import pymel.core as pm
import pymel.core.datatypes as dt

from math3d.transformation import TransformationArray
from math3d.vectorN import Vector3
from math3d.matrixN import Matrix4

from brigks.utils import attr

ICONS = ["arrow", "bone", "circle", "compass", "cross", "crossarrow", "cube", "cubewithpeak",
	"cylinder", "diamond", "flower", "jaw", "null", "pyramid", "sphere", "spine", "square",
	 "lookat", "bendedarrow", "rotatearrow", "gear", "lung"]

def transform(parent, name, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
	node = cmds.createNode("transform", name=name)
	attr.setColor(node, color)
	cmds.parent(node, parent)

	# Transform
	if tfm is not None:
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

# ----------------------------------------------------------------------------------
#  NURBS
# ----------------------------------------------------------------------------------
def cnsSurface(name="cnsSurface", parent=None, centers=[], closed=False, degree=3, width=1.0, 
																axis="z", tangent=.5, color=None):
	'''Creates a Transform node with a NurbsSurface Shape with each point constrained to a given center. 

	Args:
		name(str): Name of the newly created Node
		centers(list of path): Automatically casted when possible.
		closed(bool): Close the curve
		degree(1 or 3): degree of the curve
		width(float): Width of the surface
		axis(x, y or z): axis to align the surface to
		tangent(None or float 0-1): if not None, length of the tangents in 0-1 blend between first and next point
		color(int|list of float): color as index or rbg

	Returns:
		MFnTransformation
	'''

	if axis == "x":
		p = Vector3([width*.5, 0, 0])
		n = Vector3([-width*.5, 0, 0])
	elif axis == "y":
		p = Vector3([0, width*.5, 0])
		n = Vector3([0, -width*.5, 0])
	else:
		p = Vector3([0, 0, width*.5])
		n = Vector3([0, 0, -width*.5])
	
	ps = []
	ns = []
	for center in centers:
		matrix = cmds.xform(center, q=True, matrix=True, worldSpace=True)
		tfm = Matrix4(matrix).asTransform()

		p2 = p * tfm.rotation
		p2 += tfm.translation
		n2 = n * tfm.rotation
		n2 += tfm.translation

		ps.append(p2)
		ns.append(n2)
		
	if tangent is not None and tangent > 0:
		ps.insert(1, ps[0].lerp(ps[1], tangent))
		ps.insert(-1, ps[-2].lerp(ps[-1], 1-tangent))

		ns.insert(1, ns[0].lerp(ns[1], tangent))
		ns.insert(-1, ns[-2].lerp(ns[-1], 1-tangent))

	pcrv = curve("DELETEME_pos_crv", points=ps, closed=closed, degree=degree)
	ncrv = curve("DELETEME_neg_crv", points=ns, closed=closed, degree=degree)

	surface = cmds.loft(pcrv, ncrv, constructionHistory=False, degree=degree, name=name, 
				reverseSurfaceNormals=True, polygon=0, range=False, uniform=True)[0] 

	cmds.delete(pcrv, ncrv)
	if parent:
		cmds.parent(surface, parent)

	cmds.skinCluster(centers, surface, maximumInfluences=1, toSkeletonAndTransforms=True, bindMethod=0)
	
	return surface


def curve(name, points, closed=False, degree=3, parent=None, color=None):
	'''
		Creates a Transform node with a NurbsCurve Shape. 
		This method uses pymel for convenience but return an MFnNurbsCurve.

		I wasn't able to make it work using OM. 
		The commented code below works for kOpen, kClosed but not kPeriodic
		The issue is related to the knots. 

		knot count muyst be #CVs + degree - 1

		Args:
			name(str): Name of the newly created Node
			parent(MObject): parent of the node. None if no parent. Automatically casted when possible. 
			transform(MTransformationMatrix or MVector): Transform or position of the node
			points(list of MVector): Control points positions
			closed(bool): Close the curve
			degree(1 or 3): degree of the curve
			color(int|list of float): color as index or rbg

		Returns:
			MFnNurbsCurve
	'''
	if len(points) < 2:
		raise ValueError("You need at least 2 points")
	elif len(points) == 2:
		degree = 1
	elif len(points) == 3 and degree == 3:
		points.append(points[-1])

	if degree not in [1,3]:
		raise ValueError("Give degree must be 1 or 3")

	# Process
	if bool(closed):
		points.extend(points[:degree])
		knots = range(len(points)+degree-1)
		points = [dt.Vector(p) for p in points]
		# As much as I want to avoid pyMel, this is easier here
		pmNode = pm.curve(n=name, d=degree, p=points, per=True, k=knots)
		curve = str(pmNode)
	else:
		points = [(p[0],p[1],p[2]) for p in points]
		curve = cmds.curve(n=name, d=degree, p=points)

	if color:
		attr.setColor(curve, color)
	
	if parent:
		cmds.parent(curve, parent)

	return curve
