from maya import cmds
import json
import xml.etree.cElementTree as etree
import getpass
import datetime

from layer import Layer
from builder import Builder

DATA_ATTRIBUTE = "_userProps"

class Guide():

	def __init__(self, model=None):
		self._model = None
		self._layers = []
		self._settings = dict(characterization="None",
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
			self._model = cmds.createNode("transform", name="Guide")
			cmds.addAttr(self._model, longName="model", attributeType="bool")
			cmds.addAttr(self._model, longName="guide", attributeType="bool")
			cmds.addAttr(self._model, longName=DATA_ATTRIBUTE, dataType="string")

	def load(self, model):
		self._model = model
		if not cmds.ls(model+"."+DATA_ATTRIBUTE):
			raise RuntimeError("Invalide Guide. Missing Data Attribute.")

		# Load Settings
		data = json.loads(cmds.getAttr(model+"."+DATA_ATTRIBUTE))
		self._settings.update(data["settings"])

		# Load Layers
		for data in data["layers"]:
			layer = Layer(self, data["name"], data)
			self._layers.append(layer)

	def build(self, systemGuides):
		builder = Builder(self)
		builder.build(systemGuides)

	def dumps(self):
		return dict(settings=self._settings,
					layers=[layer.dumps() for layer in self._layers])

	def commit(self):
		# Saves settings to json in the model data attribute
		cmds.setAttr(self._model+"."+DATA_ATTRIBUTE, json.dumps(self.dumps()), type="string")

	# ----------------------------------------------------------------------------------
	# LAYERS, SYSTEMS
	# ----------------------------------------------------------------------------------
	def model(self):
		return self._model

	def setSettings(self, settings):
		self._settings.update(settings)

	def layers(self):
		return {layer.name():layer for layer in self._layers}

	def addLayer(self, name):
		layer = Layer(self, name)
		self._layers.append(layer)
		return layer

	def removeLayer(self, layer):
		index = self._layers.index(layer)
		return self._layers.pop(index)

	def findSystem(self, key):
		for layer in self._layers:
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
		xmlRoot.set("settings", json.dumps(self._settings))

		for layerName, layer in self._layers.iteritems():
			xmlRoot.append(layer.toXml(layerName))

		return xmlRoot

	@classmethod
	def fromXml(cls, path):
		guide = cls()

		tree = etree.parse(path)
		xmlRoot = tree.getroot()

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", "{}"))
		guide.setSettings(settings)

		# Load Layers
		for xmlLayer in xmlRoot:
			layer = Layer.fromXml(guide, xmlLayer)

		guide.commit()

		return guide
