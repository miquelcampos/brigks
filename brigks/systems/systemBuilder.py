from collections import OrderedDict
import itertools

from maya import cmds

from brigks.utils import attr, create, compounds
from brigks.core import naming 

class SystemBuilder():

	def __init__(self, coreBuilder, guide):
		self.coreBuilder = coreBuilder
		self.guide = guide
		self.settings = self.guide.settings
		self.setSettings = self.guide.setSettings
		self._connections = self.guide._connections
		self.attributeNames = []

		self.key = self.guide.key
		self.transforms = self.guide.transforms
		self.translations = self.guide.translations
		self.directions = self.guide.directions
		self.count = self.guide.count

		# Building Steps
		# For each system we're building, each step will be processed for all the systems
		# before running the next step. This ensure all the objects have been created 
		# before we start connecting systems together.
		# Having Attributes created after the Operators, allow us to recreate and reconnect attributes if needed
		self.steps = OrderedDict()
		self.steps["Create Objects"] = self.stepObjects
		self.steps["Create Attributes"] = self.stepAttributes
		self.steps["Create Operators"] = self.stepOperators
		self.steps["Connect System"] = self.stepConnections
		self.steps["Post Process"] = self.stepPost

	# ----------------------------------------------------------------------------------
	#  SETTINGS
	# ----------------------------------------------------------------------------------
	def negate(self):
		return self.settings("location") == "R"

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
		if self.settings("addJoints"):
			self.createJoints()

	def stepOperators(self):
		self.createOperators()

	def stepAttributes(self):
		self.deleteAttributes()
		self.createAttributes()

	def stepConnections(self):
		# Init Connections
		for slot, cnx in self._connections.iteritems():
			cnx.setBuilder(self)
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
		for slot, cnx in self._connections.iteritems():
			cnx.connect(self, slot)

	# ----------------------------------------------------------------------------------
	#  OBJECTS / ATTRIBUTES
	# ----------------------------------------------------------------------------------
	def createTransform(self, parent, part, usage, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		parent = parent if parent is not None else self.coreBuilder.localCtl
		name = self.getObjectName(usage, part)
		node = create.transform(parent, name, tfm)
		if icon:
			create.icon(icon, node, size, po, ro, so)
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
		return create.joint(parent, name, tfm=None, color=None)

	def createSurfaceJoints(self, surface, count, part="Strap"):
		parent = surface
		joints = [self.createJoint(parent, "{}{}".format(part,i)) for i in xrange(1, count+1)]
		
		# Disconnect the deformer if there is a left over constraint
		for jnt in joints:
			connections = cmds.listConnections(jnt, destination=True)
			if connections:
				srfAttach = [node for node in connections if cmds.nodeType(node) == "SurfaceMultiAttach"]
				if srfAttach:
					cmds.delete(srfAttach)

		# 0 Parametric, 1 Percentage, 2 Fixed Length
		name = self.getObjectName("Rig", "Srf")
		compounds.surfaceMultiAttach([joints], surface, attach=0, evenly=True)

		for jnt in joints:
			cmds.connectAttr(self.coreBuilder.localCtl+".sx" ,jnt+".sx")
			cmds.connectAttr(self.coreBuilder.localCtl+".sx" ,jnt+".sy")
			cmds.connectAttr(self.coreBuilder.localCtl+".sx" ,jnt+".sz")

		return joints

	def _createAttr(self, parent, displayName, attrType, value=None, minValue=None, maxValue=None,
			keyable=False, writable=True, readable=True, channelBox=True):

		longName = self.getObjectName("Rig", displayName)
		a = attr.create(parent, longName, attrType, value, minValue, maxValue,
					keyable, writable, readable, channelBox, displayName)
		self.attributeNames.append(longName)
		return a

	def createAnimAttr(self, name, attrType, value,
			minValue=None, maxValue=None, sugMinimum=None, sugMaximum=None, keyable=True):

		parent = self.coreBuilder.localCtl
		a = self._createAttr(parent, name, attrType, value,
					minValue, maxValue, keyable, writable=True)
		return a

	def createSetupAttr(self, name, attrType, value,
			minValue=None, maxValue=None, sugMinimum=None, sugMaximum=None,
			keyable=False, writable=False):

		parent = self.coreBuilder.localCtl
		a = self._createAttr(parent, name, attrType, value,
					minValue, maxValue, keyable, writable)
		return a

	def _createNode(self, nodeType, name):
		name = self.getObjectName("Nde", name)
		return cmds.createNode(nodeType, name=name)

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def getObjectName(self, usage, part):
		return naming.getObjectName(
			usage=usage,
			location=self.settings("location"),
			name=self.settings("name"),
			part=part)

	def getNodeName(self, part):
		return naming.getObjectName(
			usage="Nde",
			location=self.settings("location"),
			name=self.settings("name"),
			part=part)

	def getObject(self, usage, part):
		return self.getObjectName(usage, part)

	def getObjectFromSlot(self, slot):
		slots = self.guide.connectionSlots()
		if slot in slots:
			usage, part = slots[slot]
			return self.getObject(usage, part)

