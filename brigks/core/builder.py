import json
from maya import cmds

from datetime import datetime as dt

from brigks.core import naming

DATA_ATTRIBUTE = "_userProps"

class Builder():

	def __init__(self, guide):
		self.guide = guide
		self.systems = {}
		self._settings = dict(systems={})

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def build(self, systemGuides):
		self.buildCore()
		if not systemGuides:
			return

		start = dt.now()
		superstart = dt.now()

		# Init all the systems that needs to be built
		toBuild = {}
		for systemGuide in systemGuides:
			systemGuide.loadMarkers()

			# If marker is X, we create a Left and Right builder
			if systemGuide.settings()["location"] == "X":
				leftSystem, rightSystem = systemGuide.splitSymmetry()
				toBuild[leftSystem.key()] = leftSystem.builder(self)
				toBuild[rightSystem.key()] = rightSystem.builder(self)
			else:
				toBuild[systemGuide.key()] = systemGuide.builder(self)

		print "INIT BUILD SYSTEMS", dt.now() - start, len(toBuild)
		start = dt.now()

		# Init the systems that needs to be connected
		toConnect = {}
		for key, settings in self._settings["systems"].iteritems():
			if key in toBuild:
				continue


			if settings["split"]:
				key = key[:-1] + "X"
				systemGuide = self.guide.findSystem(key)
				systemGuide.loadMarkers()
				leftSystem, rightSystem = systemGuide.splitSymmetry()
				toConnect[leftSystem.key()] = leftSystem.builder(self)
				toConnect[rightSystem.key()] = rightSystem.builder(self)
			else:
				systemGuide = self.guide.findSystem(key)
				systemGuide.loadMarkers()

				# TODO: So we should filter to only build the connect on systems that are connected to the toBuild systems
				# How fast can we do that?
				# That seem to be plenty fast enough
				for cnx in systemGuide.connections.values():
					for otherKey in cnx.getTargetSystems():
						if otherKey in toBuild:
							break
				else:
					continue

				toConnect[key] = systemGuide.builder(self)

		print "INIT CONNECT SYSTEMS", dt.now() - start, len(toConnect)

		self.systems.update(toBuild)
		self.systems.update(toConnect)

		# Getting all the building steps
		steps = self.systems.values()[0].steps.keys()
		for step in steps:
			start = dt.now()
			
			if step == "Connect System":
				builders = toBuild.values() + toConnect.values()
			else:
				builders = toBuild.values()

			for builder in builders:
				builder.steps[step]()
			
			print step, dt.now() - start


		# Saving the keys of the systems that have been built
		newSystemsData = {}
		for k, v in self.systems.iteritems():
			newSystemsData[k] = dict(settings=v.settings(), attributes=v.attributeNames)

		self._settings["systems"].update(newSystemsData)
		self.dumps()

		print "DONE", dt.now() - superstart

	def delete(self, systemGuide):
		pass

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def buildCore(self):
		self.model = self._createModel()
		self.globalCtl = self._createController(self.model, part="Global")
		self.localCtl = self._createController(self.globalCtl, part="Local")

	def dumps(self):
		data = self._settings
		cmds.setAttr(self.model+"."+DATA_ATTRIBUTE, json.dumps(data), type="string")

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

