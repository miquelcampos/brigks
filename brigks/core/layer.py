from maya import cmds
import xml.etree.cElementTree as etree
import json

from ..systems import getSystemGuideClass
from brigks.core import naming

class Layer():

	def __init__(self, guide, data={}):
		self.guide = guide
		self.settings = dict(keepInSegmented=False,
							 expanded=False,
							 layerColor=[.875,.875,.250],
							 useLayerColor=False,
							 colorRFk=[0,.25,.75], colorRIk=[0,.5,1], 
							 colorMFk=[.5,.25,.5], colorMIk=[.85,.6,.85],
							 colorLFk=[.6,.2,.2],  colorLIk=[1,.35,.35], 
							 rigLayer=1, 
							 rigSubLayer=3)
		self.layers = dict()
		self.systems = dict()

		if data:
			self.load(data)

	def load(self, data):
		self.settings.update(data["settings"])

		# Loading Systems
		for key, systemData in data["systems"].iteritems():
			SystemClass = getSystemGuideClass(systemData["systemType"])
			system = SystemClass.load(self, systemData)
			self.systems[key] = system

		# Loading Sub Layers
		for name, data in data["layers"].iteritems():
			subLayer = Layer(self.guide, data)
			self.layers[name] = subLayer

	def dumps(self):
		data = dict(settings=self.settings,
					layers={name:layer.dumps() for name, layer in self.layers.iteritems()},
					systems={key:system.dumps() for key, system in self.systems.iteritems()} )
		return data

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def addLayer(self, name):
		# Making sure the name of the system is unique to the layer
		inputName = name
		i = 1
		while name in self.layers:
			name = inputName + str(i)
			i += 1

		layer = Layer(self.guide)
		self.layers[name] = layer
		return layer

	def findSystem(self, key):
		if key in self.systems.keys():
			return self.systems[key]

		for layer in self.layers.values():
			system = layer.findSystem(key)
			if system:
				return system

	def addSystem(self, systemType, location, name, matrices={}, version=-1):
		"""Add a new system guide to the layer

		Args:
		    systemType (str): Type of system to be create.
		    location (str): Location of the system (L/R/M/X).
		    name (str): Name of the system.
		    matrices (dict of matrix): Matrices are flat lists of coordonate.
		    version (int): Version of the system (-1 for latest).

		Returns:
		    SystemGuide: The newly created system.
		"""

		# Making sure the key of the system is unique to the guide
		inputName = name
		i = 1
		key = naming.getSystemKey(location, name)
		while self.guide.findSystem(key) is not None:
			name = inputName + str(i)
			key = naming.getSystemKey(location, name)
			i += 1

		SystemClass = getSystemGuideClass(systemType, version)
		system = SystemClass.create(self, location, name, matrices)
		self.systems[system.key()] = system

		return system

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def toXml(self, name):
		xmlRoot = etree.Element("Layer")
		xmlRoot.set("name", name)
		xmlRoot.set("settings", json.dumps(self.settings))

		for layerName, layer in self.layers.iteritems():
			xmlRoot.append(layer.toXml(layerName))

		for systemKey, system in self.systems.iteritems():
			xmlRoot.append(system.toXml())

		return xmlRoot

	@classmethod
	def fromXml(cls, guide, xmlRoot):
		layer = cls(guide)

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", "{}"))
		layer.settings.update(settings)

		for xmlObject in xmlRoot:
			if xmlObject.tag == "Layer":
				name = xmlObject.get("name")
				subLayer = Layer.fromXml(guide, xmlObject)
				layer.layers[name] = subLayer
			elif xmlObject.tag == "System":
			 	key = xmlObject.get("key")
			 	systemType = xmlObject.get("type")
				SystemClass = getSystemGuideClass(systemType)
				system = SystemClass.fromXml(layer, xmlObject)
				layer.systems[key] = system

		return layer

