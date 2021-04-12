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
		self._model = None
		self._systems = {}
		self._settings = dict(systems={})

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	def systems(self, key=None):
		return self._systems if key is None else self._systems[key]

	def builtSystems(self, key=None):	
		return self._settings["systems"] if key is None else self._settings["systems"][key]

	def model(self):
		return self._model

	# ----------------------------------------------------------------------------------
	# BUILD / DELETE
	# ----------------------------------------------------------------------------------
	def build(self, systemGuides):
		self._initCore()

		start = dt.now()
		superstart = dt.now()

		# Init all the systems that needs to be built
		self._systems = self._initSystems()
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

	def delete(self, systemGuides):
		self._initCore(create=False)
		# If there is no model, thewre is nothing to delete
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
	def _initCore(self, create=True):
		self._model = self._createModel(create)
		self.globalCtl = self._createController(self._model, part="Global", create=create)
		self.localCtl = self._createController(self.globalCtl, part="Local", create=create)

	def _initSystems(self):
		builders = {}
		# Looping over all the systems that have already been built 
		for key, settings in self.builtSystems().iteritems():

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
				builders[key] = systemGuide.builder(self)
		return builders

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
		for key, settings in self.builtSystems().iteritems():
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
				for cnx in systemGuide.connections().values():
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
			v.setSettings(attributes=v.attributeNames)
			newSystemsData[k] = v.settings()
		self.builtSystems().update(newSystemsData)

		data = self._settings
		cmds.setAttr(self._model+"."+DATA_ATTRIBUTE, json.dumps(data), type="string")

	# ----------------------------------------------------------------------------------
	# CREATE
	# ----------------------------------------------------------------------------------
	def _createModel(self, create=True):
		connections = cmds.listConnections(self.guide.model()+".model", type="transform", destination=False)
		if connections:
			model = connections[0]
		elif not create:
			return
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

	def _createController(self, parent, part, create):
		name = naming.getObjectName(naming.USAGES["Controller"], "M", "Root", part)

		exisiting = [x for x in cmds.ls(name, long=True) if x.startswith("|"+self._model)]
		if exisiting:
			controller = cmds.ls(exisiting)[0]
		elif not create:
			return
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
			this_model=self._model,
			this_guide=self.guide
			)
		exec(value, args, args)