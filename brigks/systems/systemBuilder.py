from collections import OrderedDict
import itertools

from maya import cmds

from brigks.core.useful import createTransform, createJoint, createAttr, createIcon
from brigks.core import naming 


class SystemBuilder():

	def __init__(self, coreBuilder, guide):
		self.coreBuilder = coreBuilder
		self.guide = guide
		self.key = self.guide.key
		self._settings = self.guide._settings
		self.attributeNames = []

		# Building Steps
		# For each system we're building, each step will be processed for all the systems
		# before running the next step. This ensure all the objects have been created 
		# before we start connecting systems together.
		# Having Attributes created after the Operators, allow us to recreate and reconnect attributes if needed
		self.steps = OrderedDict()
		self.steps["Create Objects"] = self.stepObjects
		self.steps["Create Operators"] = self.stepOperators
		self.steps["Create Attributes"] = self.stepAttributes
		self.steps["Connect System"] = self.stepConnections
		self.steps["Post Process"] = self.stepPost

	# ----------------------------------------------------------------------------------
	#  SETTINGS
	# ----------------------------------------------------------------------------------
	def settings(self):
		return self._settings
		
	def negate(self):
		return self._settings["location"] == "R"

	def sign(self):
		return "-" if self.negate() else ""

	def nsign(self):
		return "" if self.negate() else "-"

	def factor(self):
		return -1 if self.negate() else 1

	# ----------------------------------------------------------------------------------
	# BUILDING STEPS
	# ----------------------------------------------------------------------------------
	def stepObjects(self):
		self.deleteobjects()
		self.createObjects()
		if self._settings["addJoints"]:
			self.createJoints()

	def stepOperators(self):
		self.createOperators()

	def stepAttributes(self):
		self.deleteAttributes()
		self.createAttributes()

	def stepConnections(self):
		self.createConnections()

	def stepPost(self):
		pass

	# ----------------------------------------------------------------------------------
	# BUILDING STEPS
	# ----------------------------------------------------------------------------------
	def deleteobjects(self):
		search = self.getObject("*", "*")
		parent = cmds.ls(self.coreBuilder.localCtl, long=True)[0]
		toDelete = [x for x in cmds.ls(search, type="transform", long=True) if x.startswith(parent)]
		if toDelete:
			# Unparent all the children
			children = cmds.listRelatives(toDelete, children=True, path=True)
			children = [x for x in cmds.ls(children, long=True) if x not in toDelete]
			if children:
				cmds.parent(children, self.coreBuilder.localCtl)

			# Delete objects
			cmds.delete(toDelete)

	def createObjects(self):
		pass

	def createJoints(self):
		pass

	def createOperators(self):
		pass

	def deleteAttributes(self):
		pass
		# search = self.getObjectName(naming.USAGES["Rig"], "")
		# attributes = cmds.ls("*."+search+"*")
		# if attributes:
		# 	cmds.deleteAttr(attributes)

	def createAttributes(self):
		pass

	def createConnections(self):
		for slot, cnx in self.guide.connections.iteritems():
			cnx.connect(self, slot)

	# ----------------------------------------------------------------------------------
	#  OBJECTS / ATTRIBUTES
	# ----------------------------------------------------------------------------------
	def createTransform(self, parent, part, usage, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		parent = parent if parent is not None else self.coreBuilder.localCtl
		name = self.getObjectName(usage, part)
		node = createTransform(parent, name, tfm)
		if icon:
			createIcon(icon, node, size, po, ro, so)
		return node

	def createController(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		usage = naming.USAGES["Controller"]
		return self.createTransform(parent, part, usage, tfm, icon, size, po, ro, so, color)

	def createBuffer(self, parent, part, tfm=None):
		usage = naming.USAGES["Buffer"]
		icon = "cube"
		size = .2
		color = [0,0,0]
		return self.createTransform(parent, part, usage, tfm, icon, size, color=color)

	def createRig(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		usage = naming.USAGES["Rig"]
		color = [0,0,0]
		return self.createTransform(parent, part, usage, tfm, icon, size, po, ro, so, color)

	def createJoint(self, parent, part):
		usage = naming.USAGES["Joint"]
		color = [1,0,0]
		parent = parent if parent is not None else self.coreBuilder.localCtl
		name = self.getObjectName(usage, part)
		return createJoint(parent, name, tfm=None, color=None)

	def _createAttr(self, parent, displayName, attrType, value=None, minValue=None, maxValue=None,
			keyable=False, writable=True, readable=True, channelBox=True):

		longName = self.getObjectName("Rig", displayName)
		attr = createAttr(parent, longName, attrType, value, minValue, maxValue,
					keyable, writable, readable, channelBox, displayName)
		self.attributeNames.append(longName)
		return attr

	def createAnimAttr(self, name, attrType, value,
			minValue=None, maxValue=None, sugMinimum=None, sugMaximum=None, keyable=True):

		parent = self.coreBuilder.localCtl
		attr = self._createAttr(parent, name, attrType, value,
					minValue, maxValue, keyable, writable=True)
		return attr

	def createSetupAttr(self, name, attrType, value,
			minValue=None, maxValue=None, sugMinimum=None, sugMaximum=None,
			keyable=False, writable=False):

		parent = self.coreBuilder.localCtl
		attr = self._createAttr(parent, name, attrType, value,
					minValue, maxValue, keyable, writable)
		return attr

	def _createNode(self, nodeType, name):
		name = self.getObjectName("Nde", name)
		return cmds.createNode(nodeType, name=name)

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def getObjectName(self, usage, part):
		return naming.getObjectName(
			usage=usage,
			location=self._settings["location"],
			name=self._settings["name"],
			part=part)

	def getNodeName(self, part):
		return naming.getObjectName(
			usage="Nde",
			location=self._settings["location"],
			name=self._settings["name"],
			part=part)

	def getObject(self, usage, part):
		return self.getObjectName(usage, part)

	def getObjectFromSlot(self, slot):
		slots = self.guide.connectionSlots()
		if slot in slots:
			usage, part = slots[slot]
			return self.getObject(usage, part)

