from maya import cmds
import copy
import xml.etree.cElementTree as etree
import json

from math3d.transformation import Transformation
from math3d import TransformationArray, Vector3Array

from brigks.connections import getSystemConnectionClass
from brigks.core import naming
from brigks.utils import create
from brigks.systems.systemMarker import SystemMarker, checkMarkersMinMax


scriptDefaultValue = '''# cmds returns the maya.cmds module
# this_model returns the root node
# this_guide returns the system guide
'''

class SystemGuide(object):

	markerNames = ()
	markerPicked = ()
	markerMinMax = {}
	markerPositions = {}
	# Marker Compatibility.
	# Key is the type of systems compatible
	# Value is a dictionary of markers to rename
	# ie: markerCompatibility = dict(basic=dict(Bone="Part"))
	# In this example the system is compatible with the chain, but markers 'Bone', must be renamed to 'Part'
	markerCompatibility = {}
	compatibles = ()

	def __init__(self, layer, name="Name", location="M"):
		self._layer = layer
		self._settings = dict(
					version=[1,0,0],
					preScriptPath="",
					preScriptValue=scriptDefaultValue,
					postScriptPath="",
					postScriptValue=scriptDefaultValue,
					name=name,
					location=location,
					split=False,
					inheritColors=True,
					colorIk=[1,0,0],
					colorFk=[0,0,1],
					createJoints=True)
		self._markers = None
		self._multiMarkers = dict() 
		self._connections = {}
		self.addSettings()


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
		markers = []
		for part, matrix in checkMarkersMinMax(matrices, system.markerNames, system.markerMinMax):
			if matrix is None:
				position = cls.markerPositions[part]
				transform = Transformation.fromParts(translation=position)
				matrix = transform.asMatrix().tolist()
				matrix = [j for sub in matrix for j in sub]
			name = system.getMarkerName(part)
			marker = SystemMarker.create(name, system, parent, matrix)
			parent = marker
			markers.append(marker.name())
		if len(markers) > 1:
			curve = create.cnsCurve(system.getMarkerName("DispCrv"), markers, degree=1)
			cmds.setAttr(curve+".template", True)

		system.loadMarkers(force=True)
		system.addSettings()

		return system

	@classmethod
	def load(cls, layer, data):
		system = cls(layer)
		system.setSettings(**data["settings"])

		for slot, connectionData in data["connections"].iteritems():
			Connection = getSystemConnectionClass(connectionData["type"])
			connection = Connection()
			connection.setSettings(**connectionData["settings"])
			system._connections[slot] = connection

		return system


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
		return self.__module__.split(".")[-3]

	def version(self):
		return self.__module__.split('.')[-2]

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	def setSettings(self, **settings):
		self._settings.update(settings)

	def layer(self):
		return self._layer

	def setLayer(self, layer):
		if layer == self._layer:
			return 

		self._layer.popSystem(self)
		layer._systems.append(self)
		self._layer = layer

	# ----------------------------------------------------------------------------------
	# BUILD / DELETE / DUPLICATE
	# ----------------------------------------------------------------------------------
	def build(self):
		self.guide().build([self])

	def delete(self, deleteGuide=False):
		self.guide().delete([self], deleteGuide)

	def duplicate(self, mirror=False):
		self.loadMarkers(force=True)
		matrices = {part:marker.transformWithScale() for part, marker in self.markers().iteritems()}
		location = self._settings["location"]
		name = self._settings["name"]
		layer = self.layer()
		if mirror:
			if location not in "LR":
				raise RuntimeError("Can't Mirror Central Guide")

			matrices = {part:marker.transformWithScale().mirrored() for part, marker in self.markers().iteritems()}
			location = "R" if location == "L" else "L"

		name = self.guide().findNextSystemName(name, location)
		dupSystem = self.create(layer, location, name, matrices)
		settings = copy.deepcopy(self.settings())
		settings.pop("name")
		settings.pop("location")
		dupSystem.setSettings(**settings)

		self.layer().appendSystem(dupSystem)

		return dupSystem

	def mirror(self):
		self.loadMarkers(force=True)
		location = self._settings["location"]
		location = "R" if location == "L" else "L"
		name = self._settings["name"]

		mirrorGuide = self.guide().findSystem(naming.getSystemKey(location, name))
		if not mirrorGuide:
			return

		mirrorGuide.loadMarkers(force=True)
		matrices = {part:marker.transformWithScale().mirrored() for part, marker in self.markers().iteritems()}

		for part, marker in mirrorGuide.markers().iteritems():
			if part in matrices:
				marker.setTransform(matrices[part])

		mirrorGuide.setSettings(**self.settings())
		mirrorGuide.setSettings(location=location)

		return mirrorGuide

	def split(self):
		# This is the Method that create two symmetrical system out of one X system
		if self._settings["location"] != "X":
			raise RuntimeError("Can't split non-X System") 

		leftSystem = copy.deepcopy(self)
		rightSystem = copy.deepcopy(self)

		leftSystem.setSettings(location="L", split=True)
		rightSystem.setSettings(location="R", split=True)

		# Make sure connections are pointing to the left and right systems
		for connection in leftSystem.connections().values():
			connection.split("L")
		for connection in rightSystem.connections().values():
			connection.split("R")

		for part, marker in rightSystem.markers().iteritems():
			rightSystem.markers()[part].setMirrored(True)

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

	def addConnection(self, port, connectionType):
		if port not in self.connectionPorts():
			msg = "No such port ({p} - {x}) for this system ({k} - {t})"
			raise ValueError(msg.format(p=port, x=connectionType, k=self.key(), t=self.type()))
		elif connectionType not in self.connectionPorts()[port]:
			msg = "{st}:{p} connection has invalid type ({x}), supported types {ct}"
			raise ValueError(msg.format(st=self.type(), p=port, x=connectionType, ct=self.connectionPorts()[port]))

		Connection = getSystemConnectionClass(connectionType)
		connection = Connection()
		self._connections[port] = connection
		return connection

	def deleteConnection(self, port):
		if port in self._connections:
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
	def rename(self, location, name):
		self.loadMarkers(force=True)

		for part, marker in self._markers.iteritems():
			newName = self.getMarkerName(part, location, name)
			marker.rename(newName)

		self._settings["location"] = location
		self._settings["name"] = name

		# TODO Rename Connections
		# # Connections
		# for system in self.guide().systems():
		# 	pass

		self.guide().commit()

	def loadMarkers(self, force=False):
		if self._markers is None or force:
			self._markers = dict()
			self._multiMarkers = dict()
			search = self.getMarkerName("*")
			markers = cmds.ls(search, type="transform", long=True)
			markers = [m for m in markers if m.startswith("|"+self.model())]
			for marker in markers:
				part = marker.split("_")[-1]
				self._markers[part] = SystemMarker(marker, self)

	def markers(self, name=None):
		self.loadMarkers()
		if name is None:
			return self._markers
		elif name in self.markerMinMax:
			if name not in self._multiMarkers:
				self._multiMarkers[name] = []
				markerMin, markerMax = self.markerMinMax[name]
				limit = lambda x: x <= markerMax if markerMax > 0 else lambda i: True
				i = 1
				while limit(i):
					part = "{}{}".format(name, i)
					if part not in self._markers:
						break
					self._multiMarkers[name].append(self._markers[part])
					i += 1
			return self._multiMarkers[name]
		else:
			return self._markers[name]

	def swapMarkers(self, systemType):
		for oldPart, newPart in self.markerCompatibility[systemType].iteritems():
			if oldPart in self.markerMinMax:
				markerMin, markerMax = self.markerMinMax[oldPart]
				limit = lambda x: x <= markerMax if markerMax > 0 else lambda i: True
				i = 1
				while limit(i):
					oldName = self.getMarkerName("{}{}".format(oldPart, i))
					newName = self.getMarkerName("{}{}".format(newPart, i))
					if not cmds.objExists(oldName):
						break
					cmds.rename(oldName, newName)
					i += 1
			else:
				oldName = self.getMarkerName(oldPart)
				newName = self.getMarkerName(newPart)
				if cmds.objExists(oldName):
					cmds.rename(oldName, newName)

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

	def scales(self, name=None):
		if name is None:
			return {k:m.scale() for k,m in self.markers().iteritems()}
		elif name in self.markerMinMax:
			return Vector3Array([m.scale() for m in self.markers(name)])
		else:
			return self.markers(name).scale()

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

	def getMarkerName(self, part, location=None, name=None):
		use = "Gde"
		location = location if location is not None else self._settings["location"]
		name = name if name is not None else self._settings["name"]
		return naming.getObjectName(use, location, name, part)

	def deleteMarkers(self):
		self.loadMarkers(force=True)
		markers = [m.name() for m in self._markers.values()]
		if markers:
			cmds.delete(markers)

	# ----------------------------------------------------------------------------------
	# IMPORT EXPORT
	# ----------------------------------------------------------------------------------
	def toXml(self):
		self.loadMarkers()

		xmlRoot = etree.Element("System")
		xmlRoot.set("type", self.type())
		xmlRoot.set("version", self.version())
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
		# system = cls(layer)

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
		system.setSettings(**settings)

		# Connections
		xmlConnections = xmlRoot.findall("Connection")
		xmlConnections = {xmlCnx.get("port"):xmlCnx for xmlCnx in xmlConnections}
		for port, xmlConnection in xmlConnections.iteritems():
		 	connectionType = xmlConnection.get("type")
		 	settings = json.loads(xmlConnection.get("settings"))
			cnx = system.addConnection(port, connectionType)
			cnx.setSettings(**settings)

			# Connection = getSystemConnectionClass(connectionType)
			# connection = Connection.fromXml(xmlConnection)
			# system._connections[port] = connection

		return system
