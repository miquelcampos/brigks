from maya import cmds
import copy
import xml.etree.cElementTree as etree
import json

from math3d.transformation import Transformation
from math3d import TransformationArray, Vector3Array

from brigks.connections import getSystemConnectionClass
from brigks.core import naming
from brigks.systems.systemMarker import SystemMarker, checkMarkersMinMax


class SystemGuide(object):

	markerNames = ("Part",)
	markerPicked = ("Part",)
	markerMinMax = dict(Part=(1,-1))
	defaultPositions = {}
	compatibles = ()

	def __init__(self, layer):
		self._layer = layer
		self._settings = dict(
					version=[1,0,0],
					name="Name",
					location="X",
					split=False,
					inheritColors=True,
					colorIk=[1,0,0],
					colorFk=[0,0,1],
					addJoints=True)
		self.addSettings()

		self._connections = {}

		self._markers = None
		self._aMarkers = dict()
		# self._transforms = dict()
		# self._aTransforms = None
		# self._positions = dict()
		# self._aPositions = None

	@classmethod
	def create(cls, layer, location, name, matrices=None):
		"""Create System Guide

		Args:
		    systemType (str): Type of system to be create.
		    location (str): Location of the system (L/R/M/X).
		    name (str): Name of the system.
		    version (int): Version of the system (-1 for latest).
		    matrices (dict of matrix): Matrices are flat lists of coordonate.

		Returns:
		    SystemGuide: The newly created system.
		"""
		system = cls(layer)
		system._settings["location"] = location
		system._settings["name"] = name

		# Create Markers
		parent = system.model()
		for name, matrix in checkMarkersMinMax(matrices, system.markerNames, system.markerMinMax):
			if matrix is None:
				position = cls.defaultPositions[name]
				transform = Transformation.fromParts(translation=position)
				matrix = transform.asMatrix().tolist()
				matrix = [j for sub in matrix for j in sub]
			name = system.getMarkerName(name)
			SystemMarker.create(name, parent, matrix)

		return system

	@classmethod
	def load(cls, layer, data):
		system = cls(layer)
		system.setSettings(data["settings"])

		for slot, connectionData in data["connections"].iteritems():
			Connection = getSystemConnectionClass(connectionData["type"])
			connection = Connection()
			connection.setSettings(connectionData["settings"])
			system._connections[slot] = connection

		return system

	def build(self):
		self.guide().build([self])

	def dumps(self):
		"""
		Returns:
		    dictionary: System settings, including connections.
		"""
		data = dict(systemType=self.type(),
					settings=self._settings,
					connections={slot:cnx.dumps() for slot, cnx in self._connections.iteritems()})
		return data

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def guide(self):
		return self._layer.guide()

	def model(self):
		return self._layer.guide().model()

	def key(self):
		return naming.getSystemKey(self._settings["location"], self._settings["name"])

	def type(self):
		return self.__module__.split(".")[-2]

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	def setSettings(self, settings):
		self._settings.update(settings)

	def setLayer(self, layer):
		if layer == self._layer:
			return 

		self._layer.removeSystem(self)
		layer._systems.append(self)
		self._layer = layer

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def splitSymmetry(self):
		# This is the Method that create two symmetrical system out of one X system
		if self._settings["location"] != "X":
			RuntimeError("Can't splitSymmetry non-X System") 

		leftSystem = copy.deepcopy(self)
		rightSystem = copy.deepcopy(self)

		leftSystem.settings["location"] = "L"
		leftSystem.settings["split"] = True
		rightSystem.settings["location"] = "R"
		rightSystem.settings["split"] = True

		# Make sure connections are pointing to the left and right systems
		for connection in leftSystem.connections.values():
			connection.splitSymmetry("L")
		for connection in rightSystem.connections.values():
			connection.splitSymmetry("R")

		for part, marker in rightSystem.markers.iteritems():
			rightSystem.markers[part][0] *= -1

		return leftSystem, rightSystem

	def builder(self, parentBuilder):
		from brigks.systems import getSystemBuilderClass
		SystemBuilder = getSystemBuilderClass(self.type())
		return SystemBuilder(parentBuilder, self)

	# ----------------------------------------------------------------------------------
	# CONNECTIONS
	# ----------------------------------------------------------------------------------
	def connections(self, key=None):
		return self._connections if key is None else self._connections[key]

	def addConnection(self, connectionType, port):
		Connection = getSystemConnectionClass(connectionType)
		connection = Connection()
		self._connections[port] = connection
		return connection

	def deleteConnection(self, port):
		self._connections.pop(port)

	def connectionPorts(self):
		# Returns the ports as a dictionary of portName, connectionsTypes
		self.loadMarkers()
		return {}

	def connectionSlots(self):
		# Returns the slots as a dictionary of slotName, objectUsage/objectPart
		self.loadMarkers()
		return {}

	# ----------------------------------------------------------------------------------
	# MARKERS / TRANSFORMS
	# ----------------------------------------------------------------------------------
	def loadMarkers(self):
		if self._markers is None:
			self._markers = dict()
			search = self.getMarkerName("*")
			markers = cmds.ls(search, type="transform", long=True)
			markers = [m for m in markers if m.startswith("|"+self.model())]
			for marker in markers:
				part = marker.split("_")[-1]
				self._markers[part] = SystemMarker(marker)

	def markers(self, name=None):
		self.loadMarkers()
		if name is None:
			return self._markers
		elif name in self.markerMinMax:
			if name not in self._aMarkers:
				self._aMarkers[name] = []
				markerMin, markerMax = self.markerMinMax[name]
				limit = lambda x: x <= markerMax if markerMax > 0 else lambda i: True
				i = 1
				while limit(i):
					part = "{}{}".format(name, i)
					if part not in self._markers:
						break
					self._aMarkers[name].append(self._markers[part])
					i += 1
			return self._aMarkers[name]
		else:
			return self._markers[name]

	def transforms(self, name=None):
		if name is None:
			return {k:m.transform() for k,m in self.markers().iteritems()}
		elif name in self.markerMinMax:
			return TransformationArray([m.transform() for m in self.markers(name)])
		else:
			return self.markers(name).transform()

	def translations(self, name=None):
		if name is None:
			return {k:m.translation() for k,m in self.markers().iteritems()}
		elif name in self.markerMinMax:
			return Vector3Array([m.translation() for m in self.markers(name)])
		else:
			return self.markers(name).translation()

	def directions(self, name=None, axis="x"):
		if name is None:
			return {k:m.direction(axis) for k,m in self.markers().iteritems()}
		elif name in self.markerMinMax:
			return Vector3Array([m.direction(axis) for m in self.markers(name)])
		else:
			return self.markers(name).direction(axis)

	def count(self, name):
		if name not in self.markerMinMax:
			raise RuntimeError("Can't count single Markers")
		return len(self.markers(name))

	# def createMarker(self, name, matrix=None):
	# 	name = self.getMarkerName(name)
	# 	node = cmds.spaceLocator(name=name)
	# 	if matrix:
	# 		cmds.xform(node, matrix=matrix, worldSpace=True)
	# 	cmds.parent(node, self.model())

	def getMarkerName(self, part):
		return naming.getObjectName("Gde",
					self._settings["location"],
					self._settings["name"],
					part)

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def toXml(self):
		self.loadMarkers()

		xmlRoot = etree.Element("System")
		xmlRoot.set("type", self.type())
		xmlRoot.set("key", self.key())
		xmlRoot.set("settings", json.dumps(self._settings))

		for port, connection in self._connections.iteritems():
			xmlRoot.append(connection.toXml(port))

		for markerName, position in self._markers.iteritems():
			xmlMarker = etree.SubElement(xmlRoot, "Marker")
			xmlMarker.set("name", markerName)
			xmlMarker.set("position", json.dumps(position))

		return xmlRoot

	@classmethod
	def fromXml(cls, layer, xmlRoot):
		system = cls(layer)

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", {}))

		# Markers Transforms
		xmlMarkers = xmlRoot.findall("Marker")
		matrices = {}
		for xmlMarker in xmlMarkers:
			name = xmlMarker.get("name")
			matrix = json.loads(xmlMarker.get("matrix"))
			matrices[name] = matrix

		name = settings["name"]
		location = settings["location"]

		# Create the system
		system = cls.create(layer, location, name, matrices)
		system.setSettings(settings)

		# Connections
		xmlConnections = xmlRoot.findall("Connection")
		xmlConnections = {xmlCnx.get("port"):xmlCnx for xmlCnx in xmlConnections}
		for port, xmlConnection in xmlConnections.iteritems():
		 	connectionType = xmlConnection.get("type")
			Connection = getSystemConnectionClass(connectionType)
			connection = Connection.fromXml(xmlConnection)
			system._connections[port] = connection

		return system
