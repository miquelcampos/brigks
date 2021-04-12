from maya import cmds
import xml.etree.cElementTree as etree
import json

from ..systems import getSystemGuideClass
from brigks.core import naming

class Layer():

	def __init__(self, parent, name, data={}):
		self._parent = parent
		self._name = None
		self._layers = [] # Sub Layers
		self._systems = []
		self._settings = dict(keepInSegmented=False,
							 expanded=False,
							 layerColor=[.875,.875,.250],
							 useLayerColor=False,
							 inheritColors=True,
							 colorRFk=[0,.25,.75], colorRIk=[0,.5,1], 
							 colorMFk=[.5,.25,.5], colorMIk=[.85,.6,.85],
							 colorLFk=[.6,.2,.2],  colorLIk=[1,.35,.35], 
							 rigLayer=1, 
							 rigSubLayer=3)

		# Makes sure the name is unique
		self.setName(name)

		if data:
			self.load(data)

	def load(self, data):
		self._settings.update(data["settings"])

		# Loading Systems
		for systemData in data["systems"]:
			SystemClass = getSystemGuideClass(systemData["systemType"])
			system = SystemClass.load(self, systemData)
			self._systems.append(system)

		# Loading Sub Layers
		for data in data["layers"]:
			layer = Layer(self, data["name"], data)
			self._layers.append(layer)

	def build(self):
		self.guide().build(self._systems)

	def delete(self, deleteGuide=False):
		self.guide().delete(self._systems, deleteGuide)

	def dumps(self):
		data = dict(name=self._name,
					settings=self._settings,
					layers=[layer.dumps() for layer in self._layers],
					systems=[system.dumps() for system in self._systems] )
		return data

	# ----------------------------------------------------------------------------------
	# NAME and LAYERS
	# ----------------------------------------------------------------------------------
	def guide(self):
		if isinstance(self._parent, Layer):
			return self._parent.guide()
		else:
			return self._parent

	def settings(self):
		return self._settings

	def setSettings(self, **settings):
		self._settings.update(settings)

	def name(self):
		return self._name

	def setName(self, name):
		name = self.__findUniqueName(name, self._parent.layers())
		self._name = name

	def layers(self):
		return {layer.name():layer for layer in self._layers}

	def addLayer(self, name):
		layer = Layer(self, name)
		self._layers.append(layer)
		return layer

	def removeLayer(self, layer):
		index = self._layers.index(layer)
		return self._layers.pop(index)

	def setParent(self, parent=None):
		if parent == self._parent:
			return 

		if parent is None:
			parent = self.guide()

		self._parent.removeLayer(self)

		self._parent = parent
		self.setName(self.name())
		self._parent._layers.append(self)

	def __findUniqueName(self, name, layers):
		inputName = name
		i = 1
		while name in layers:
			name = inputName + str(i)
			i += 1
		return name

	# ----------------------------------------------------------------------------------
	# SYSTEMS
	# ----------------------------------------------------------------------------------
	def systems(self):
		return {system.key():system for system in self._systems}

	def findSystem(self, key):
		for system in self._systems:
			if system.key() == key:
				return system

		for layer in self._layers:
			system = layer.findSystem(key)
			if system:
				return system

	def addSystem(self, systemType, location, name, matrices={}, version=None):
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
		while self.guide().findSystem(key) is not None:
			name = inputName + str(i)
			key = naming.getSystemKey(location, name)
			i += 1

		SystemClass = getSystemGuideClass(systemType, version)
		system = SystemClass.create(self, location, name, matrices)
		self._systems.append(system)

		return system

	def popSystem(self, system):
		index = self._systems.index(system)
		return self._systems.pop(index)

	def swapSystem(self, oldSystem, systemType, version):
		oldSystem.swapMarkers(systemType)
		self.popSystem(oldSystem)

		SystemClass = getSystemGuideClass(systemType, version)
		newSystem = SystemClass(self)
		newSystem.setSettings(**oldSystem.settings())

		self._systems.append(newSystem)
		return newSystem


	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def toXml(self):
		xmlRoot = etree.Element("Layer")
		xmlRoot.set("name", layer.name())
		xmlRoot.set("settings", json.dumps(self._settings))

		for layer in self._layers:
			xmlRoot.append(layer.toXml(layer))

		for system in self._systems:
			xmlRoot.append(system.toXml())

		return xmlRoot

	@classmethod
	def fromXml(cls, parent, xmlRoot):
		name = xmlRoot.get("name")
		settings = json.loads(xmlRoot.get("settings", "{}"))

		layer = parent.addLayer(name)
		layer.setSettings(**settings)

		for xmlObject in xmlRoot:
			if xmlObject.tag == "Layer":
				name = xmlObject.get("name")
				subLayer = Layer.fromXml(layer, xmlObject)
				layer._layers.append(subLayer)
			elif xmlObject.tag == "System":
			 	key = xmlObject.get("key")
			 	systemType = xmlObject.get("type")
			 	systemVersion = xmlObject.get("type")
				SystemClass = getSystemGuideClass(systemType, systemVersion)
				system = SystemClass.fromXml(layer, xmlObject)
				layer._systems.append(system)

		return layer

