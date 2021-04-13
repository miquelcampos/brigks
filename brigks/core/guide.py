from maya import cmds
import json
import xml.etree.cElementTree as etree
import getpass
import datetime

from layer import Layer
from builder import Builder
from brigks.core.config import DATA_ATTRIBUTE
from brigks.utils.xmldom import indent


scriptDefaultValue = '''# cmds returns the maya.cmds module
# this_model returns the root node
# this_guide returns the guide
'''

class Guide():

	def __init__(self, model=None):
		self._model = None
		self._layers = []
		self._settings = dict(version=[1,0,0],
							preScriptPath="",
							preScriptValue=scriptDefaultValue,
							postScriptPath="",
							postScriptValue=scriptDefaultValue
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

	def build(self, systemGuides=None):
		if systemGuides is None:
			systemGuides = self._getAllSystems()

		builder = Builder(self)
		builder.build(systemGuides)

	def delete(self, systemGuides=None, deleteGuide=False):
		if systemGuides is None:
			systemGuides = self._getAllSystems()

		builder = Builder(self)
		builder.delete(systemGuides)

		if deleteGuide:
			for systemGuide in systemGuides:
				systemGuide.layer().popSystem(systemGuide)
				systemGuide.deleteMarkers()

			self.commit()

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

	def setup(self):
		connections = cmds.listConnections("Guide.model", destination=False, type="transform")
		if connections:
			return connections[0]

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	def setSettings(self, **settings):
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

	def _getAllSystems(self):	
		systemGuides = []
		for layer in self._layers:
			systems = layer.systems().values()
			systemGuides.extend(systems)
		return systemGuides

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def write(self, path):
		xmlRoot = self.toXml()
		indent(xmlRoot)
		tree = etree.ElementTree(xmlRoot)
		tree.write(path)

	def toXml(self):
		xmlRoot = etree.Element("Guide")
		xmlRoot.set("user", getpass.getuser())
		xmlRoot.set("date", str(datetime.datetime.now()))
		xmlRoot.set("settings", json.dumps(self._settings))

		for layer in self._layers:
			xmlRoot.append(layer.toXml())

		return xmlRoot

	@classmethod
	def fromXml(cls, path):
		guide = cls()

		tree = etree.parse(path)
		xmlRoot = tree.getroot()

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", "{}"))
		guide.setSettings(**settings)

		# Load Layers
		for xmlLayer in xmlRoot:
			layer = Layer.fromXml(guide, xmlLayer)

		guide.commit()

		return guide
