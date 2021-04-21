import os.path
import itertools
from collections import OrderedDict

from maya import cmds

from brigks.utils import attributes, create, compounds
from brigks import naming, config

class SystemBuilder():

	def __init__(self, coreBuilder, guide):
		self.coreBuilder = coreBuilder
		self.nodes = self.coreBuilder.nodes
		self.model = self.coreBuilder.model
		self.guide = guide
		self.settings = self.guide.settings
		self.setSettings = self.guide.setSettings
		self._connections = self.guide._connections
		self.attributeNames = []
		self._uiHosts = {}

		self.key = self.guide.key
		self.type = self.guide.type
		self.markers = self.guide.markers
		self.transforms = self.guide.transforms
		self.translations = self.guide.translations
		self.directions = self.guide.directions
		self.scales = self.guide.scales
		self.count = self.guide.count

		# Building Steps
		# For each system we're building, each step will be processed for all the systems
		# before running the next step. This ensure all the objects have been created 
		# before we start connecting systems together.
		# Having Attributes created after the Operators, allow us to recreate and reconnect attributes if needed
		self.steps = OrderedDict()
		self.steps["Pre Script"] = self.stepPreScript
		self.steps["Create Objects"] = self.stepObjects
		self.steps["Create Attributes"] = self.stepAttributes
		self.steps["Create Operators"] = self.stepOperators
		self.steps["Connect System"] = self.stepConnections
		# self.steps["Post Process"] = self.stepPostProcess
		self.steps["Post Script"] = self.stepPostScript

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

	def colorIk(self):
		return [0,0,1]

	def colorFk(self):
		return [0,0,1]

	def connections(self, key=None, includeUIHosts=False):
		if includeUIHosts:
			connections = self._connections
		else:
			connections = {k:v for k, v in self._connections.iteritems() if v.type() != "uiHost"}
		return connections if key is None else connections[key]
		
	# ----------------------------------------------------------------------------------
	# BUILDING STEPS
	# ----------------------------------------------------------------------------------
	def stepPreScript(self):
		self.executeScript(self.settings("preScriptPath"), self.settings("preScriptValue"))

	def stepObjects(self):
		self.preDeleteObjects()
		self.deleteObjects()
		self.createObjects()
		if self.settings("createJoints"):
			self.createJoints()

	def stepOperators(self):
		self.createOperators()

	def stepAttributes(self):
		self.deleteAttributes()

		# Get UIHost
		for port, cnx in self._connections.iteritems():
			if cnx.type() == "uiHost":
				cnx.setBuilder(self)
				self._uiHosts[port] = cnx.getHost()

		self.createAttributes()

	def stepConnections(self):
		# Init Connections
		for slot, cnx in self.connections(includeUIHosts=False).iteritems():
			cnx.setBuilder(self)
		self.createConnections()

	def stepPostProcess(self):
		pass

	def stepPostScript(self):
		self.executeScript(self.settings("postScriptPath"), self.settings("postScriptValue"))

	# ----------------------------------------------------------------------------------
	# BUILDING STEPS
	# ----------------------------------------------------------------------------------
	def preDeleteObjects(self):
		pass
		
	def deleteObjects(self):
		search = self.getObjectName("*", "*")
		parent = cmds.ls(self.nodes("local"), long=True)[0]
		toDelete = [x for x in cmds.ls(search, type="transform", long=True) if x.startswith(parent)]
		if toDelete:
			# Unparent all the children
			children = cmds.listRelatives(toDelete, children=True, type="transform", path=True)
			children = [x for x in cmds.ls(children, long=True) if x not in toDelete]
			if children:
				cmds.parent(children, self.nodes("local"))

			# Delete objects
			cmds.delete(toDelete)

		# Delete Utility Nodes
		search = self.getObjectName(config.USE_NDE, "*")
		toDelete = cmds.ls(search, long=True)
		if toDelete:
			cmds.delete(toDelete)

	def createObjects(self):
		pass

	def deleteJoints(self):
		search = self.getObjectName(config.USE_JNT, "*")
		parent = cmds.ls(self.nodes("local"), long=True)[0]
		toDelete = [x for x in cmds.ls(search, type="joint", long=True) if x.startswith(parent)]
		if toDelete:
			# Unparent all the children
			children = cmds.listRelatives(toDelete, children=True, type="transform", path=True)
			children = [x for x in cmds.ls(children, long=True) if x not in toDelete]
			if children:
				cmds.parent(children, self.nodes("local"))

			# Delete objects
			cmds.delete(toDelete)

	def createJoints(self):
		pass

	def createOperators(self):
		pass

	def deleteAttributes(self):
		if self.key() in self.coreBuilder.builtSystems():
			settings = self.coreBuilder.builtSystems(self.key())
			for name in settings["attributes"]:
				attr = cmds.ls("*."+name)
				if attr:
					cmds.deleteAttr(attr)

	def createAttributes(self):
		pass

	def createConnections(self):
		pass

	def executeScript(self, path, value):
		if os.path.exists(path):
			with open(path, "r") as f:
				value = f.read()

		args = dict(
			cmds=cmds,
			this_model=self.model(),
			this_guide=self.guide
			)
		exec(value, args, args)

	def delete(self):
		self.deleteObjects()
		self.deleteJoints()
		self.deleteAttributes()

	# ----------------------------------------------------------------------------------
	#  HELPERS to CREATE OBJECTS / ATTRIBUTES
	# ----------------------------------------------------------------------------------
	def addTransform(self, parent, part, use, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		parent = parent if parent is not None else self.nodes("local")
		name = self.getObjectName(use, part)
		node = create.transform(name, parent, tfm, color=color)
		if icon:
			create.icon(icon, node, size, po, ro, so)
		return node

	def addCtl(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		color = [0,0,1]
		return self.addTransform(parent, part, config.USE_CTL, tfm, icon, size, po, ro, so, color)

	def addBfr(self, parent, part, tfm=None):
		icon = "cube"
		size = .2
		color = [0,0,0]
		return self.addTransform(parent, part, config.USE_BFR, tfm, icon, size, color=color)

	def addRig(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		color = [0,0,0]
		return self.addTransform(parent, part, config.USE_RIG, tfm, icon, size, po, ro, so, color)

	def addJnt(self, parent, part, reference=None):
		name = self.getObjectName(config.USE_JNT, part)
		parent = parent if parent is not None else self.nodes("local")
		matrix = cmds.xform(parent, q=True, matrix=True, worldSpace=True)
		color = [1,0,0]

		jnt = create.joint(name, parent, matrix, color, radius=.5)

		# Bind Pose reference
		if reference:
			attr = jnt+"."+config.BINDPOSE_ATTRIBUTE
			if not cmds.ls(attr):
				cmds.addAttr(jnt, longName=config.BINDPOSE_ATTRIBUTE, dataType="matrix")

			cmds.connectAttr(reference+".worldInverseMatrix[0]", attr, force=True)

			done = []
			for connection in cmds.listConnections(jnt, type="skinCluster", plugs=True) or []:
				skinCluster, skinClusterAttr = connection.split(".") 
				if skinCluster in done:
					continue
				index = int(skinClusterAttr.split("[")[-1][:-1])
				cmds.connectAttr(attr, skinCluster+".bindPreMatrix[{}]".format(index), force=True)
				done.append(skinCluster)

		return jnt

	def addCamera(self, parent, part, tfm=None, color=None, **kwargs):
		name = self.getObjectName(config.USE_CTL, part)
		parent = parent if parent is not None else self.nodes("local")

		return create.camera(name, parent, matrix=tfm, color=color, **kwargs)

	def addSurfaceJnts(self, surface, count, part="Strap"):
		parent = surface
		joints = [self.addJnt(parent, "{}{}".format(part,i)) for i in xrange(1, count+1)]
		
		# Disconnect the deformer if there is a left over constraint
		for jnt in joints:
			connections = cmds.listConnections(jnt, destination=True)
			if connections:
				srfAttach = [node for node in connections if cmds.nodeType(node) == "SurfaceMultiAttach"]
				if srfAttach:
					cmds.delete(srfAttach)

		# 0 Parametric, 1 Percentage, 2 Fixed Length
		self.addCompound("surfaceMultiAttach", "JntSrf", [joints], surface, attach=0, evenly=True)

		for jnt in joints:
			cmds.connectAttr(self.nodes("local")+".sx" ,jnt+".sx")
			cmds.connectAttr(self.nodes("local")+".sx" ,jnt+".sy")
			cmds.connectAttr(self.nodes("local")+".sx" ,jnt+".sz")

		return joints

	def addAttr(self, host, shortName, attrType, value=None, minValue=None, maxValue=None,
			keyable=False, writable=True, readable=True, channelBox=True):
		longName = self.getObjectName(config.USE_RIG, shortName)
		a = attributes.create(host, longName, attrType, value, minValue, maxValue,
					keyable, writable, readable, channelBox, shortName)
		self.attributeNames.append(longName)
		return a

	def addAnimAttr(self, name, attrType, value,
			minValue=None, maxValue=None, sugMinimum=None, sugMaximum=None, keyable=True):
		# For now we only support one UIHost, but we could 
		# pass an argument for which host to crete the attr to

		if "UI" not in self._uiHosts:
			self._uiHosts["UI"] = self.addRig(self.nodes("setup"), "Anim")
			attributes.setKeyables(self._uiHosts["UI"], [])

		a = self.addAttr(self._uiHosts["UI"], name, attrType, value,
					minValue, maxValue, keyable, writable=True)
		return a

	def addSetupAttr(self, name, attrType, value,
			minValue=None, maxValue=None, sugMinimum=None, sugMaximum=None,
			keyable=True, writable=True):

		if "Setup" not in self._uiHosts:
			self._uiHosts["Setup"] = self.addRig(self.nodes("setup"), "Setup")
			attributes.setKeyables(self._uiHosts["Setup"], [])

		a = self.addAttr(self._uiHosts["Setup"], name, attrType, value,
					minValue, maxValue, keyable, writable)
		return a

	def addNode(self, nodeType, name):
		name = self.getObjectName(config.USE_NDE, name)
		return cmds.createNode(nodeType, name=name)

	def addCompound(self, compoundType, name, *args, **kwargs):
		method = compounds.__dict__[compoundType]
		name = self.getObjectName(config.USE_NDE, name+"{node}")
		return method(name, *args, **kwargs)

	# ----------------------------------------------------------------------------------
	# GET OBJECTS and NAMES
	# ----------------------------------------------------------------------------------
	def getObjectName(self, use, part):
		return naming.getObjectName(
			use=use,
			location=self.settings("location"),
			name=self.settings("name"),
			part=part)

	def getNodeName(self, part):
		return naming.getObjectName(
			use=config.USE_NDE,
			location=self.settings("location"),
			name=self.settings("name"),
			part=part)

	def getObject(self, use, part):
		name = self.getObjectName(use, part)
		objects = [x for x in cmds.ls(name, type="transform", long=True) if x.startswith("|"+self.model())]
		if objects:
			return objects[0]

	def getNode(self, use, part):
		name = self.getObjectName(config.USE_NDE, part)
		nodes = cmds.ls(name)
		if nodes:
			return nodes[0]

	def getObjectFromSlot(self, slot):
		slots = self.guide.connectionSlots()
		if slot in slots:
			use, part = slots[slot]
			return self.getObject(use, part)

	def getAttribute(self, shortName):
		longName = self.getObjectName(config.USE_RIG, shortName)
		attributes = [x for x in cmds.ls("*."+longName, long=True) if x.startswith("|"+self.model())]
		if attributes:
			return attributes[0]

