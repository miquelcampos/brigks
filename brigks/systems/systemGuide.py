from maya import cmds
import copy
import xml.etree.cElementTree as etree
import json

from tools.marbie.connections import getSystemConnectionClass
from tools.marbie.core import naming
from tools.marbie.systems.systemMarker import SystemMarker, checkMarkersMinMax


class SystemGuide(object):

	markerNames = ("Part",)
	markerPicked = ("Part",)
	markerMinMax = dict(Part=(1,-1))

	def __init__(self, layer):
		self.layer = layer
		self.settings = dict(
					version=[1,0,0],
					name="Name",
					location="X",
					split=False,
					colorIk=[1,0,0],
					colorFk=[0,0,1],
					option1=True,
					option2=True,
					option3=True,
					option4=True,
					option5=True,
					option6=True,
					option7=True,
					option8=True,
					option9=True,
					option10=True,
					option11=True,
					option12=True,
					option13=True,
					option14=True,
					option15=True)
		self.addSettings()

		self.connections = {}
		self.coreGuide = self.layer.guide

	@classmethod
	def create(cls, layer, location, name):
		system = cls(layer)
		system.settings["location"] = location
		system.settings["name"] = name

		# Create Markers
		parent = system.layer.guide.model
		for name, x in checkMarkersMinMax({}, system.markerNames, system.markerMinMax):
			name = system.getMarkerName(name)
			SystemMarker.create(name, parent)

		return system

	@classmethod
	def load(cls, layer, data):
		system = cls(layer)
		system.settings.update(data["settings"])

		for slot, connectionData in data["connections"].iteritems():
			Connection = getSystemConnectionClass(connectionData["type"])
			connection = Connection()
			connection.setConnection(connectionData["settings"])
			system.connections[slot] = connection

		return system

	def dumps(self):
		data = dict(systemType=self.type(),
					settings=self.settings,
					connections={slot:cnx.dumps() for slot, cnx in self.connections.iteritems()})
		return data

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def key(self):
		return naming.getSystemKey(self.settings["location"], self.settings["name"])

	def type(self):
		return self.__module__.split(".")[-2]

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def splitSymmetry(self):
		# This is the Method that create two symmetrical system out of one X system
		if self.settings["location"] != "X":
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
		from tools.marbie.systems import getSystemBuilderClass
		SystemBuilder = getSystemBuilderClass(self.type())
		return SystemBuilder(parentBuilder, self)

	# ----------------------------------------------------------------------------------
	# CONNECTIONS
	# ----------------------------------------------------------------------------------
	def addConnection(self, connectionType, port):
		Connection = getSystemConnectionClass(connectionType)
		connection = Connection()
		self.connections[port] = connection
		return connection

	def deleteConnection(self, port):
		self.connections.pop(port)

	def connectionPorts(self):
		# Returns the ports as a dictionary of portName, connectionsTypes
		self.loadMarkers()
		return {}

	def connectionSlots(self):
		# Returns the slots as a dictionary of slotName, objectUsage/objectPart
		self.loadMarkers()
		return {}

	# ----------------------------------------------------------------------------------
	# MARKERS
	# ----------------------------------------------------------------------------------
	def loadMarkers(self):
		self.markers = {}
		search = self.getMarkerName("*")
		markers = cmds.ls(search, type="transform", long=True)
		markers = [m for m in markers if m.startswith("|"+self.coreGuide.model)]
		for marker in markers:
			part = marker.split("_")[-1]
			self.markers[part] = SystemMarker(marker)

	# def createMarker(self, name, matrix=None):
	# 	name = self.getMarkerName(name)
	# 	node = cmds.spaceLocator(name=name)
	# 	if matrix:
	# 		cmds.xform(node, matrix=matrix, worldSpace=True)
	# 	cmds.parent(node, self.layer.guide.model)

	def getMarkerName(self, part):
		return naming.getObjectName("Gde",
					self.settings["location"],
					self.settings["name"],
					part)

	def count(self, part):
		return 1

	# ----------------------------------------------------------------------------------
	# TRANSFORM
	# ----------------------------------------------------------------------------------
	def transforms(self, key):
		if key in self.markers:
			return self.markers[key].transform()

	def translations(self, key):
		if key in self.markers:
			return self.markers[key].translation()

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def toXml(self):
		self.loadMarkers()

		xmlRoot = etree.Element("System")
		xmlRoot.set("type", self.type())
		xmlRoot.set("key", self.key())
		xmlRoot.set("settings", json.dumps(self.settings))

		for port, connection in self.connections.iteritems():
			xmlRoot.append(connection.toXml(port))

		for markerName, position in self.markers.iteritems():
			xmlMarker = etree.SubElement(xmlRoot, "Marker")
			xmlMarker.set("name", markerName)
			xmlMarker.set("position", json.dumps(position))

		return xmlRoot

	@classmethod
	def fromXml(cls, layer, xmlRoot):
		system = cls(layer)

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", {}))
		system.settings.update(settings)

		# Markers
		xmlMarkers = xmlRoot.findall("Marker")
		xmlMarkers = {xmlMarker.get("name"):xmlMarker for xmlMarker in xmlMarkers}

		parent = system.layer.guide.model
		for name, xmlMarker in checkMarkersMinMax(xmlMarkers, system.markerNames, system.markerMinMax):
			if xmlMarker is not None:
			 	matrix = json.loads(xmlMarker.get("matrix"))
			else:
				print "NotFound", system.key(), system.type(), name, xmlMarkers.keys()
				matrix = None

			name = system.getMarkerName(name)
			SystemMarker.create(name, parent, matrix)

		# Connections
		xmlConnections = xmlRoot.findall("Connection")
		xmlConnections = {xmlCnx.get("port"):xmlCnx for xmlCnx in xmlConnections}
		for port, xmlConnection in xmlConnections.iteritems():
		 	connectionType = xmlConnection.get("type")
			Connection = getSystemConnectionClass(connectionType)
			connection = Connection.fromXml(xmlConnection)
			system.connections[port] = connection

		return system
