import json
import os.path
import logging
from datetime import datetime as dt

from maya import cmds

from brigks.core import naming
from brigks.core.config import DATA_ATTRIBUTE

class Builder():

	def __init__(self, guide):
		self.guide = guide
		self._systems = {}
		self._settings = dict(systems={})

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	def systems(self, key=None):
		return self._systems if key is None else self._systems[key]

	# ----------------------------------------------------------------------------------
	# BUILD
	# ----------------------------------------------------------------------------------
	def build(self, systemGuides):
		self._buildCore()

		start = dt.now()
		superstart = dt.now()

		# Init all the systems that needs to be built
		toBuild = self._initSystemsToBuild(systemGuides)

		logging.info("INIT BUILD SYSTEMS {time}".format(time=dt.now() - start))
		start = dt.now()

		# Init the systems that needs to be connected
		toConnect = self._initSystemsToConnect(toBuild)
		logging.info("INIT CONNECT SYSTEMS {time}".format(time=dt.now() - start))

		self._systems.update(toBuild)
		self._systems.update(toConnect)

		# Pre Script
		self._executeScript(self.guide.settings("preScriptPath"), self.guide.settings("preScriptValue"))
		logging.info("PRE SCRIPT {time}".format(time=dt.now() - start))

		# Getting all the building steps and then build
		if self._systems:
			self._buildSystems(toBuild, toConnect)

		# Saving the keys of the systems that have been built
		self._commit()

		# Post Script
		self._executeScript(self.guide.settings("postScriptPath"), self.guide.settings("postScriptValue"))
		logging.info("POST SCRIPT {time}".format(time=dt.now() - start))

		logging.info("DONE {time}".format(time=dt.now() - superstart))

	def delete(self, systemGuide):
		pass

	# ----------------------------------------------------------------------------------
	# BUILD HELPERS
	# ----------------------------------------------------------------------------------
	def _buildCore(self):
		self.model = self._createModel()
		self.globalCtl = self._createController(self.model, part="Global")
		self.localCtl = self._createController(self.globalCtl, part="Local")

	def _initSystemsToBuild(self, systemGuides):
		builders = {}
		for systemGuide in systemGuides:
			systemGuide.loadMarkers()

			# If marker is X, we create a Left and Right builder
			if systemGuide.settings()["location"] == "X":
				leftSystem, rightSystem = systemGuide.splitSymmetry()
				builders[leftSystem.key()] = leftSystem.builder(self)
				builders[rightSystem.key()] = rightSystem.builder(self)
			else:
				builders[systemGuide.key()] = systemGuide.builder(self)
		return builders

	def _initSystemsToConnect(self, toBuild):
		builders = {}
		# Looping over all the systems that have already been built 
		for key, settings in self._settings["systems"].iteritems():
			if key in toBuild:
				continue

			if settings["split"]:
				key = key[:-1] + "X"
				systemGuide = self.guide.findSystem(key)
				systemGuide.loadMarkers()
				leftSystem, rightSystem = systemGuide.splitSymmetry()
				builders[leftSystem.key()] = leftSystem.builder(self)
				builders[rightSystem.key()] = rightSystem.builder(self)
			else:
				systemGuide = self.guide.findSystem(key)
				systemGuide.loadMarkers()

				# Check if any of those systems are connected to something we're rebuilding
				for cnx in systemGuide.connections.values():
					for otherKey in cnx.getTargetSystems():
						if otherKey in toBuild:
							break
				else:
					continue

				builders[key] = systemGuide.builder(self)
		return builders

	def _buildSystems(self, toBuild, toConnect):
		steps = self._systems.values()[0].steps.keys()
		for step in steps:
			start = dt.now()
			
			if step == "Connect System":
				builders = toBuild.values() + toConnect.values()
			else:
				builders = toBuild.values()

			for builder in builders:
				logging.info("{key} {step}".format(key=builder.key(), step=step))
				builder.steps[step]()
			
			logging.info("{step} Completed in {time}".format(step=step, time=dt.now() - start))

	def _commit(self):
		# Update with the latest data
		newSystemsData = {}
		for k, v in self._systems.iteritems():
			newSystemsData[k] = dict(settings=v.settings(), attributes=v.attributeNames)
		self._settings["systems"].update(newSystemsData)

		data = self._settings
		cmds.setAttr(self.model+"."+DATA_ATTRIBUTE, json.dumps(data), type="string")

	# ----------------------------------------------------------------------------------
	# CREATE
	# ----------------------------------------------------------------------------------
	def _createModel(self):
		connections = cmds.listConnections(self.guide.model()+".model", type="transform", destination=False)
		if connections:
			model = connections[0]
		else:
			model = cmds.createNode("transform", name="Setup")
	
		if not cmds.ls(model+".model"):
			cmds.addAttr(model, longName="model", attributeType="bool")
		if not cmds.ls(model+"."+DATA_ATTRIBUTE):
			cmds.addAttr(model, longName=DATA_ATTRIBUTE, dataType="string")

		# Loading the data from the model
		data = cmds.getAttr(model+"."+DATA_ATTRIBUTE)
		if data:
			self._settings.update(json.loads(data))
	
		# Connecting the Setup to the Guide. This is how we track which model is used to build the guide
		cmds.connectAttr(model+".model", self.guide.model()+".model", force=True)
		return model

	def _createController(self, parent, part):
		name = naming.getObjectName(naming.USAGES["Controller"], "M", "Root", part)

		exisiting = [x for x in cmds.ls(name, long=True) if x.startswith("|"+self.model)]
		if exisiting:
			controller = cmds.ls(exisiting)[0]
		else:
			controller = cmds.createNode("transform", name=name)
	
		currentParent = cmds.listRelatives(controller, parent=True, path=True)
		if not currentParent or currentParent[0] != parent:
			cmds.parent(controller, parent)
		return controller

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def _executeScript(self, path, value):
		if os.path.exists(path):
			with open(path, "r") as f:
				value = f.read()

		args = dict(
			cmds=cmds,
			this_model=self.model,
			this_guide=self.guide
			)
		exec(value, args, args)