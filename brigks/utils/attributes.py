from maya import cmds

from brigks.utils import constants

# ----------------------------------------------------------------------------------
# ATTRIBUTES
# ----------------------------------------------------------------------------------
def create(node, longName, dataType="bool", value=True, minValue=None, maxValue=None,
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
		attrs = constants.trs_attrs

	for attrName in constants.trs_attrs:
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