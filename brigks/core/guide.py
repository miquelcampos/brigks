from maya import cmds
import json
import xml.etree.cElementTree as etree
import getpass
import datetime

from layer import Layer

DATA_ATTRIBUTE = "_userProps"

class Guide():

	def __init__(self, model=None):
		self.model = None
		self.layers = dict() 
		self.settings = dict(characterization="None",
							version=[1,0,0],
							defaultScaling=1.0,
							synoptic=[],
							variations=[],
							resetControlLook=False,
							motionConnections=dict(mocap=None, crowd=None),
							motionRigPresets=dict(mocap='default', crowd='default'),
							motionRigNodes=dict(mocap='', crowd='')
							)

		# If we pass a model, then we load the settings
		# Otherwise we create a new Model
		if model:
			self.load(model)
		else:
			self.model = cmds.createNode("transform", name="Guide")
			cmds.addAttr(self.model, longName="model", attributeType="bool")
			cmds.addAttr(self.model, longName="guide", attributeType="bool")
			cmds.addAttr(self.model, longName=DATA_ATTRIBUTE, dataType="string")

	def load(self, model):
		self.model = model
		if not cmds.ls(model+"."+DATA_ATTRIBUTE):
			raise RuntimeError("Invalide Guide. Missing Data Attribute.")

		# Load Settings
		data = json.loads(cmds.getAttr(model+"."+DATA_ATTRIBUTE))
		self.settings.update(data["settings"])

		# Load Layers
		for name, data in data["layers"].iteritems():
			layer = Layer(self, data)
			self.layers[name] = layer

	def dumps(self):
		return dict(settings=self.settings,
					layers={name:layer.dumps() for name, layer in self.layers.iteritems()})

	def commit(self):
		# Saves settings to json in the model data attribute
		cmds.setAttr(self.model+"."+DATA_ATTRIBUTE, json.dumps(self.dumps()), type="string")

	# ----------------------------------------------------------------------------------
	# LAYERS, SYSTEMS
	# ----------------------------------------------------------------------------------
	def addLayer(self, name):
		# Making sure the name of the system is unique to the layer
		inputName = name
		i = 1
		while name in self.layers:
			name = inputName + str(i)
			i += 1

		layer = Layer(self)
		self.layers[name] = layer
		return layer

	def findSystem(self, key):
		for layer in self.layers.values():
			system = layer.findSystem(key)
			if system:
				return system

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def toXml(self):
		xmlRoot = etree.Element("Guide")
		xmlRoot.set("user", getpass.getuser())
		xmlRoot.set("date", str(datetime.datetime.now()))
		xmlRoot.set("settings", json.dumps(self.settings))

		for layerName, layer in self.layers.iteritems():
			xmlRoot.append(layer.toXml(layerName))

		return xmlRoot

	@classmethod
	def fromXml(cls, path):
		guide = cls()

		tree = etree.parse(path)
		xmlRoot = tree.getroot()

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", "{}"))
		guide.settings.update(settings)

		# Load Layers
		for xmlLayer in xmlRoot:
			name = xmlLayer.get("name")
			layer = Layer.fromXml(guide, xmlLayer)
			guide.layers[name] = layer

		guide.dumps()

		return guide
