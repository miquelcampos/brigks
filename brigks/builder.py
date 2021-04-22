import json
import os.path
import logging
from datetime import datetime as dt
import xml.etree.cElementTree as etree

from maya import cmds

from brigks import naming
from brigks import config
from brigks.utils import create

HIERARCHY_XML_PATH = os.path.join(os.path.dirname(__file__),"hierarchy.xml")

class Builder():

	def __init__(self, guide):
		self.guide = guide
		self._model = None
		self._systems = {}
		self._settings = dict(systems={})
		self._nodes = {}

		# Load
		self.load()


	def load(self):
		connections = cmds.listConnections(self.guide.model()+".model", destination=False, type="transform")
		if not connections:
			return 

		self._model = connections[0]

		# Loading the data from the model
		data = cmds.getAttr(self._model+"."+config.DATA_ATTRIBUTE)
		if data:
			self._settings.update(json.loads(data))

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def model(self):
		return self._model

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	def systems(self, key=None):
		return self._systems if key is None else self._systems[key]

	def nodes(self, key=None):
		return self._nodes if key is None else self._nodes[key]

	def builtSystems(self, key=None):	
		return self._settings["systems"] if key is None else self._settings["systems"][key]

	# ----------------------------------------------------------------------------------
	# BUILD / DELETE
	# ----------------------------------------------------------------------------------
	def build(self, systemGuides):
		self._buildCore()

		start = dt.now()
		superstart = dt.now()

		# Init all the systems that needs to be built
		self._systems = self._initSystems()
		toBuild = self._initSystemsToBuild(systemGuides)
		# Init the systems that needs to be connected
		toConnect, toCreateAttr = self._initSystemsToConnect(toBuild)
		self._systems.update(toBuild)
		self._systems.update(toConnect)
		self._systems.update(toCreateAttr)

		logging.info("INIT SYSTEMS {time}".format(time=dt.now() - start))
		start = dt.now()

		# Pre Script
		self._executeScript(self.guide.settings("preScriptPath"), self.guide.settings("preScriptValue"))
		logging.info("PRE SCRIPT {time}".format(time=dt.now() - start))
		start = dt.now()

		# Getting all the building steps and then build
		if self._systems:
			self._buildSystems(toBuild, toConnect, toCreateAttr)

		# Saving the keys of the systems that have been built
		self._commit()

		hide = []
		if self.guide.settings("hideRig"):
			hide += [x for x in cmds.ls("Rig_*", type="transform", long=True) if x.startswith("|"+self._model)]
			hide += [x for x in cmds.ls("Rig_*", type="transform", long=True) if x.startswith("|"+self._model)]
		if self.guide.settings("hideJoints"):
			hide += [x for x in cmds.ls("Jnt_*", type="transform", long=True) if x.startswith("|"+self._model)]
		for node in hide:
			cmds.setAttr(node+".lodVisibility", False)

		# Post Script
		self._executeScript(self.guide.settings("postScriptPath"), self.guide.settings("postScriptValue"))
		logging.info("POST SCRIPT {time}".format(time=dt.now() - start))

		logging.info("DONE {time}".format(time=dt.now() - superstart))

	def delete(self, systemGuides):
		# If there is no model, there is nothing to delete
		if not self._model:
			return

		# Filter out the systems that have not been built
		systemGuides = [g for g in systemGuides if g.key() in self.builtSystems()]

		toDelete = self._initSystemsToBuild(systemGuides)
		for key, system in toDelete.iteritems():
			system.delete()	

			# Removing system from meta data
			self.builtSystems().pop(key)

		self._commit()

	# ----------------------------------------------------------------------------------
	# BUILD HELPERS
	# ----------------------------------------------------------------------------------
	def _buildCore(self, create=True):
		self._model = self.addModel(create)

		xmlHierarchy = etree.parse(HIERARCHY_XML_PATH).getroot()
		for xmlNode in xmlHierarchy:
			self._createFromXml(xmlNode, parent=self._model)

	def _createFromXml(self, xmlNode, parent):
		# Parse the XML tree and create the hierachy of nodes
		key = xmlNode.get("key")
		part = xmlNode.get("part")

		if xmlNode.tag == "organizer":
			use = config.USE_ORG
		elif xmlNode.tag == "controller":
			use = config.USE_CTL

		name = naming.getObjectName(use, "M", "Root", part)

		options = dict(
			icon=xmlNode.get("icon", None))	
		for x in ["size", "po", "ro", "so", "color"]:
			value = xmlNode.get(x, None)
			if value is not None:
				options[x] = json.loads(value)
		
		node = self.addTransform(name, parent, **options)

		for xmlChild in xmlNode:
			self._createFromXml(xmlChild, node)

		self._nodes[key] = node
		return node

	def _initSystems(self):
		builders = {}
		# Looping over all the systems that have already been built 
		for key, settings in self.builtSystems().iteritems():
			if settings["split"]:
				key = key[:-1] + "X"
				systemGuide = self.guide.findSystem(key)
				systemGuide.loadMarkers(force=True)
				leftSystem, rightSystem = systemGuide.split()
				builders[leftSystem.key()] = leftSystem.builder(self)
				builders[rightSystem.key()] = rightSystem.builder(self)
			else:
				systemGuide = self.guide.findSystem(key)
				systemGuide.loadMarkers(force=True)
				builders[key] = systemGuide.builder(self)
		return builders

	def _initSystemsToBuild(self, systemGuides):
		builders = {}
		for systemGuide in systemGuides:
			systemGuide.loadMarkers(force=True)

			# If marker is X, we create a Left and Right builder
			if systemGuide.settings()["location"] == "X":
				leftSystem, rightSystem = systemGuide.split()
				builders[leftSystem.key()] = leftSystem.builder(self)
				builders[rightSystem.key()] = rightSystem.builder(self)
			else:
				builders[systemGuide.key()] = systemGuide.builder(self)
		return builders

	def _initSystemsToConnect(self, toBuild):
		toConnect = {}
		toCreateAttr = {}
		# Looping over all the systems that have already been built 
		for key, settings in self.builtSystems().iteritems():
			if key in toBuild:
				continue
			
			# TODO, WE're Re-initializing systems that have already been initialized, we can do bette rthan that

			if settings["split"]:
				key = key[:-1] + "X"
				systemGuide = self.guide.findSystem(key)
				systemGuide.loadMarkers(force=True)
				leftSystem, rightSystem = systemGuide.split()
				toConnect[leftSystem.key()] = leftSystem.builder(self)
				toConnect[rightSystem.key()] = rightSystem.builder(self)
			else:
				systemGuide = self.guide.findSystem(key)
				systemGuide.loadMarkers(force=True)

				# Check if any of those systems are connected to something we're rebuilding
				for cnx in systemGuide.connections().values():
					if key not in toCreateAttr and cnx.type() == "uiHost":
						for otherKey in cnx.getTargetSystems():
							if otherKey in toBuild:
								toCreateAttr[key] = systemGuide.builder(self)
								break
					elif key not in toConnect:
						for otherKey in cnx.getTargetSystems():
							if otherKey in toBuild:
								toConnect[key] = systemGuide.builder(self)
								break

		return toConnect, toCreateAttr

	def _buildSystems(self, toBuild, toConnect, toCreateAttr):
		steps = self._systems.values()[0].steps.keys()
		for step in steps:
			start = dt.now()
			
			if step == "Connect System":
				builders = toBuild.values() + toConnect.values()
			elif step == "Create Attributes":
				builders = toBuild.values() + toCreateAttr.values()
			else:
				builders = toBuild.values()

			for builder in builders:
				logging.debug("{step}: {key} ({type})".format(key=builder.key(), step=step, type=builder.type()))
				builder.steps[step]()
			
			logging.info("{step}: Completed in {time}".format(step=step, time=dt.now() - start))

			if self.guide.settings("stopAfter") == step:
				break

	def _commit(self):
		# Update with the latest data
		newSystemsData = {}
		for k, v in self._systems.iteritems():
			v.setSettings(attributes=v.attributeNames)
			newSystemsData[k] = v.settings()
		self.builtSystems().update(newSystemsData)

		data = self._settings
		cmds.setAttr(self._model+"."+config.DATA_ATTRIBUTE, json.dumps(data), type="string")

	# ----------------------------------------------------------------------------------
	# CREATE
	# ----------------------------------------------------------------------------------
	def addModel(self, create=True):
		model = self.addTransform("Setup")
	
		cmds.addAttr(model, longName="model", attributeType="bool")
		cmds.addAttr(model, longName=config.DATA_ATTRIBUTE, dataType="string")

		# Connecting the Setup to the Guide. This is how we track which model is used to build the guide
		cmds.connectAttr(model+".model", self.guide.model()+".model", force=True)
		return model

	def addTransform(self, name, parent=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		existing = [x for x in cmds.ls(name, long=True) if x.startswith("|"+self._model)]
		if existing:
			node = existing[0]

		node = create.transform(name, parent, color=color)
		if icon:
			if size is None:
				size = 1
			create.icon(icon, node, size, po, ro, so)
		return node
		
	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def _executeScript(self, path, value):
		if os.path.exists(path):
			with open(path, "r") as f:
				value = f.read()

		args = dict(
			cmds=cmds,
			this_model=self._model,
			this_guide=self.guide
			)
		exec(value, args, args)