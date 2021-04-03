from maya import cmds

# Constants
trs_attrs = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")


ICONS = ["arrow", "bone", "circle", "compass", "cross", "crossarrow", "cube", "cubewithpeak",
	"cylinder", "diamond", "flower", "jaw", "null", "pyramid", "sphere", "spine", "square",
	 "lookat", "bendedarrow", "rotatearrow", "gear", "lung"]


# ----------------------------------------------------------------------------------
# 3D OBJECTS
# ----------------------------------------------------------------------------------
def createTransform(parent, name, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
	node = cmds.createNode("transform", name=name)
	setColor(node, color)
	cmds.parent(node, parent)

	# Transform
	cmds.xform(node, matrix=tfm.asMatrix().flattened(), worldSpace=True)

	return node

def createJoint(parent, name, tfm=None, color=None):
	node = cmds.createNode("joint", name=name)
	setColor(node, color)
	cmds.parent(node, parent)

	# Transform
	matrix = cmds.xform(parent, q=True, matrix=True, worldSpace=True)
	cmds.xform(node, matrix=matrix, worldSpace=True)
	
	return node

def createIcon(icon, parent=None, size=1, po=None, ro=None, so=None, showCenter=False, showOrientation=False, centerScale=1.0):
	if not cmds.pluginInfo("harbieLocator.mll", q=True,  loaded=True): 
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
# ATTRIBUTES
# ----------------------------------------------------------------------------------
def createHarmonic(name, slave, master, amplitude=1.0, decay=8.0, frequency=0.5, termination=0.0, amplitudeAxis=(1,1,1)):
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

# ----------------------------------------------------------------------------------
# ATTRIBUTES
# ----------------------------------------------------------------------------------
def createAttr(node, longName, dataType="bool", value=True, minValue=None, maxValue=None,
					keyable=False, writable=True, readable=True, channelBox=True, displayName=None):
	"""Creates an attribute.

	We return an MPlug rather than an MFnAttribute because it's easy to get the MFn from
	the MPlug but impossible to go the other way round.

	Args:
		node(MObject or MFnDependencyNode): Automatically casted when possible.
		longName(str): Attribute Name
		dataType(str): ("kString")
		value(?): must be a valid type for this attribute
		keyable(bool): is keyable
		writable(bool): is writable
		readable(bool): is readable
		channelBox(bool): shows up in the channel box
		displayName(str|None): display Name of the parameter. Same as longName if None

	Returns:
		MPlug

	Raises:
		ValueError: if attibute with same name already exists
	"""
	longName = str(longName)
	displayName = longName if displayName is None else str(displayName)

	if cmds.attributeQuery(longName, node=node, exists=True):
		raise ValueError("Node already has an attribute with that name")

	if cmds.lockNode(node, query=True)[0]:
		raise RuntimeError("Given node is locked. {n}".format(n=node))

	kwargs = dict(
		longName=longName,
		niceName=displayName,
		attributeType=dataType,
		keyable=keyable,
		writable=writable,
		readable=readable )

	# For some reason string needs to be created with dataType and not attributeType
	if dataType == "string":
		kwargs["dataType"] = kwargs.pop("attributeType")

	isNumeric = dataType not in ["string", "enum"]

	if isNumeric:
		if value is not None and dataType[-1] not in "23":
			kwargs["defaultValue"] = value
		kwargs["hasMinValue"] = minValue is not None
		kwargs["hasMaxValue"] = maxValue is not None
		if minValue is not None:
			kwargs["minValue"] = minValue
		if maxValue is not None:
			kwargs["maxValue"] = maxValue

	if dataType == "enum":
		kwargs["enumName"] = ":".join(minValue)
		if isinstance(value, str):
			if value in minValue:
				value = minValue.index(value)
			else:
				raise ValueError("Value %s must be an int or in %s"%(value, minValue))
		kwargs["defaultValue"] = value

	# Process
	cmds.addAttr(node, **kwargs)

	if dataType.endswith("2") or dataType.endswith("3"):
		count = int(dataType[-1])
		kwargs["attributeType"] = dataType[:-1]
		for i in range(count):
			kwargs["longName"] = longName+str(i)
			kwargs["niceName"] = displayName+str(i)
			if value is not None:
				kwargs["defaultValue"] = value[i]
			cmds.addAttr(node, parent=longName, **kwargs)

	if not isNumeric:
		cmds.setAttr(node+"."+longName, value)

	return node+"."+longName

def setKeyables(node, attrs=None, lock=True):
	if attrs is None:
		attrs = trs_attrs

	for attrName in trs_attrs:
		keyable = attrName in attrs
		cmds.setAttr(node+"."+attrName, lock=not keyable)
		cmds.setAttr(node+"."+attrName, keyable=keyable)
		if not keyable:
			cmds.setAttr(node+"."+attrName, channelBox=keyable)


def setRotOrder(node, rotOrder):
	orders = ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]
	#TODO Parent/Unparent children? 
	matrix = cmds.xform(node, q=True, matrix=True, worldSpace=True)
	cmds.setAttr(node+".rotateOrder", orders.index(rotOrder.lower()))
	cmds.xform(node, matrix=matrix, worldSpace=True)

def setColor(node, color):
	''' Set the color of given node

	Args:
		node(): 
		color(int|float triplet): color as index or rgb(0-1)
	'''
	if color is None:
		cmds.setAttr(node+".overrideEnabled", False)
		return 

	isIndex = isinstance(color, int)
	if not isIndex and not [isinstance(c, float) for c in list(color)]:
		raise ValueError("Given color must be index or float triplet")


	cmds.setAttr(node+".overrideEnabled", True)
	cmds.setAttr(node+".overrideRGBColors", not isIndex)

	if isIndex:
		cmds.setAttr(node+".overrideColor", color)
	else:
		cmds.setAttr(node+".overrideColorR", color[0])
		cmds.setAttr(node+".overrideColorG", color[1])
		cmds.setAttr(node+".overrideColorB", color[2])



# ----------------------------------------------------------------------------------
# XML
# ----------------------------------------------------------------------------------
def indent(elem, level=0):
	i = "\n" + level*" "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + " "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i


