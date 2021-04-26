import json
import os.path
import logging
from datetime import datetime as dt
import xml.etree.cElementTree as etree

from maya import cmds

from brigks import naming
from brigks import config
from brigks.utils import create, script

HIERARCHY_XML_PATH = os.path.join(os.path.dirname(__file__),"hierarchy.xml")

class Builder():
	'''Main Builder Class

	This object is building the core rig and loops on the systems to build and connect them all
	'''

	def __init__(self, guide):
		'''Builder Init

		Args:
			guide (Guide): The Guide to build from

		Returns:
			Builder
		'''
		self.guide = guide
		self._model = None
		self._systems = {}
		self._settings = dict(systems={})
		self._nodes = {}
		
		# Search if a model for the rig has already been built
		# The model is connected to the guide using the "model" attributes
		# This is how we detect which model has been generated from the guide
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
		'''Returns the root node of the rig

		Returns:
			str
		'''
		return self._model

	def settings(self, key=None):
		'''Returns the settings of the builder 

		Args:
			key (None||str): None returns the whole dictionary, if a key is passed it returns that setting value

		Returns:
			dictionary or setting value
		'''
		return self._settings if key is None else self._settings[key]

	def systems(self, key=None):
		'''Returns the system builder

		Args:
			key (None||str): None returns the a dictionary of all the systems, if a key is passed it returns that specific system

		Returns:
			dictionary or SystemBuilder
		'''
		return self._systems if key is None else self._systems[key]

	def nodes(self, key=None):
		'''Returns the core nodes 

		The core nodes are defined in the core hierachy (See hierarchy.xml)

		Args:
			key (None||str): None returns the a dictionary of all the nodes, if a key is passed it returns that specific node

		Returns:
			dictionary or str
		'''
		return self._nodes if key is None else self._nodes[key]

	def builtSystems(self, key=None):	
		'''Returns the system settings for the systems already built

		Args:
			key (None||str): None returns the a dictionary of all the systems, if a key is passed it returns that specific system

		Returns:
			dictionary or settings
		'''
		return self._settings["systems"] if key is None else self._settings["systems"][key]

	# ----------------------------------------------------------------------------------
	# BUILD / DELETE
	# ----------------------------------------------------------------------------------
	def build(self, systemGuides):
		'''Main method to build the rig.

		This is the method find the systems already built and loops over the system to build. 
		It's building all the steps and connect all the systems together.

		Args:
			systemGuides (list of SystemGuide): The system to be built
		'''
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
		script.execute(self.guide.settings("preScriptPath"), self.guide.settings("preScriptValue"),
			 dict(cmds=cmds, this_model=self._model, this_guide=self.guide))
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
		script.execute(self.guide.settings("postScriptPath"), self.guide.settings("postScriptValue"),
			 dict(cmds=cmds, this_model=self._model, this_guide=self.guide))
		logging.info("POST SCRIPT {time}".format(time=dt.now() - start))

		logging.info("DONE {time}".format(time=dt.now() - superstart))

	def delete(self, systemGuides):
		'''Delete the given systems.
		
		# TODO This is ambiguous. The method could be renamed deleteSystems maybe?

		Args:
			systemGuides (list of SystemGuide): The system to be deleted
		'''
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
	def _buildCore(self):
		'''Private Method. Create the core hierachy of the rig
		
		The hierarchy is defined in the hierarchy.xml file
		'''
		self._model = self._addModel()

		xmlHierarchy = etree.parse(HIERARCHY_XML_PATH).getroot()
		for xmlNode in xmlHierarchy:
			self._createFromXml(xmlNode, parent=self._model)

	def _createFromXml(self, xmlNode, parent):
		'''Private Method. Create node from xml definition
		'''
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
		
		node = self._addTransform(name, parent, **options)

		for xmlChild in xmlNode:
			self._createFromXml(xmlChild, node)

		self._nodes[key] = node
		return node

	def _initSystems(self):
		'''Private Method. Initialize the SystemBuilder for systems already built

		We need those in case some need to be used in a connection

		Returns:
			dictionary: The SystemBuilder in a dictionary with the system key for index 
		'''
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
		'''Private Method. Initialize the SystemBuilder for systems that we need to build

		Returns:
			dictionary: The SystemBuilder in a dictionary with the system key for index 
		'''
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
		'''Private Method. Initialize the SystemBuilder for systems already built that need to be reconnected

		Returns:
			tupple of dictionary: First the systems to connect, then the system to createAttr
		'''
		toConnect = {}
		toCreateAttr = {}
		# Looping over all the systems that have already been built 
		for key, settings in self.builtSystems().iteritems():
			if key in toBuild:
				continue
			
			# TODO, We're Re-initializing systems that have already been initialized, we can do bette r than that

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
		'''Private Method. Loop over the system to be built and connect and run each building step

		To guarantee that objects are available, the build process is happening in steps.
		The steps are defined in the SystemBuilder class
			Pre Script
			Create Objects
			Create Attributes
			Create Operators
			Connect System
			Post Script
		'''
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
		'''Private Method. Save the settings as a json dictionary in the rig
		
		This allow us to keep track what was built with which settings. 
		This is useful when rebuilding but also when accessing the rig, when you need to know which options
		are available for a specific system.
		'''
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
	def _addModel(self):
		'''Private Method. Create the root node for the rig

		The model is a sinple transform node with a 'model' attribute
		This model attribute is connected to the guide, to keep the relation between the two
		The model also has a string attribute to hold the rig settings as a json dictionary 
		'''
		model = self._addTransform("Setup")
	
		cmds.addAttr(model, longName="model", attributeType="bool")
		cmds.addAttr(model, longName=config.DATA_ATTRIBUTE, dataType="string")

		# Connecting the Setup to the Guide. This is how we track which model is used to build the guide
		cmds.connectAttr(model+".model", self.guide.model()+".model", force=True)
		return model

	def _addTransform(self, name, parent=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		'''Private Method. Create a transform node

		Args:
			name (str): Name of the newly created node
			parent (str|None): Parent of the node
			icon (str): Icon type. See brigks.utils.create for icon list
			size (int): Size of the icon
			po (3 floats or None): Position offset of the icon
			ro (3 floats or None): Rotation offset of the icon (in degrees)
			so (3 floats or None): Scale offset of the icon
			color (3 floats or None): Color of the node RGB from 0 to 1

		Returns:
			str: The transform node
		'''
		existing = [x for x in cmds.ls(name, long=True) if x.startswith("|"+self._model)]
		if existing:
			node = existing[0]

		node = create.transform(name, parent, color=color)
		if icon:
			if size is None:
				size = 1
			create.icon(icon, node, size, po, ro, so)
		return node
