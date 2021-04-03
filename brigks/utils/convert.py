import json
import getpass
import datetime
import xml.etree.cElementTree as etree

#from math3d import Transformation, Quaternion, Vector3
import math3d.transformation as t
reload(t)
from math3d.transformation import Transformation
from math3d.quaternion import Quaternion
from math3d.vectorN import Vector3

HARBIE_TYPES = dict(
		arm01="arm",
		basic01="basic",
		bean01="quadrant",
		# breast01="breast",
		camera01="camera",
		chain01="chain",
		foot01="foot",
		leg01="leg",
		leg3bones01="zleg",
		lookAt01="lookat",
		meta01="meta",
		neck01="neck",
		params01="attribute",
		psdDriver01="psd",
		# piston="piston",
		slider01="slider",
		spine01="spine",
		stretch01="stretch",
		tracker01="tracker",
		transformAverage01="average",
		transformDriven01="driven",
		transformMulti01="multi",
		twistSpline01="twist"
	)

MARKER_NAMES = dict(
	stretch01=dict(
		Root="Part1",
		End="Part2"
		),
	lookAt01=dict(
		Root="Part1",
		Target="Part2"
		),
	bean01=dict(
		Root="Part1",
		),
	transformAverage01=dict(
		Root="Part1",
		),
	spine01=dict(
		Root="Part1",
		Eff="Part2",
		),
	slider01=dict(
		Rail1="Part1",
		Rail2="Part2",
		Rail3="Part3",
		Rail4="Part4"
		),
	leg01=dict(
		Root="Part1",
		Knee="Part2",
		Ankle="Part3",
		Eff="Part4",
		),
	arm01=dict(
		Root="Part1",
		Elbow="Part2",
		Wrist="Part3",
		Eff="Part4",
		),
	neck01=dict(
		Root="Part1",
		Head="Part2",
		Eff="Part3",
		),
	camera01=dict(
		Root="Part1",
		),
	)

COMPONENT_TYPES = dict(
	pntSubComponent="vtx",
	edgeSubComponent="edg",
	polySubComponent="fac",
	)


def convertXmlHarbie(xmlHarbie):
	xmlRoot = etree.Element("Guide")
	xmlRoot.set("user", getpass.getuser())
	xmlRoot.set("date", str(datetime.datetime.now()))

	# Settings
	xmlHarbieParameters = xmlHarbie.find("Parameters")
	settings = json.loads(xmlHarbieParameters.get("value", {}))
	xmlRoot.set("settings", json.dumps(settings))

	# Layers
	xmlHarbieLayers = xmlHarbie.find("Layers")
	for xmlHarbieLayer in xmlHarbieLayers:
		xmlLayer = _convertXmlLayer(xmlHarbieLayer)
		xmlRoot.append(xmlLayer)

	return xmlRoot


def _convertXmlLayer(xmlHarbieLayer):
	xmlLayer = etree.Element("Layer")
	xmlLayer.set("name", xmlHarbieLayer.get("name"))

	xmlHarbieParameters = xmlHarbieLayer.find("Parameters")
	settings = json.loads(xmlHarbieParameters.get("value", {}))
	xmlLayer.set("settings", json.dumps(settings))

	xmlHarbieSystems = xmlHarbieLayer.find("Systems")
	for xmlHarbieSystem in xmlHarbieSystems:
		xmlSystem = _convertXmLSystem(xmlHarbieSystem)
		if xmlSystem:
			xmlLayer.append(xmlSystem)

	return xmlLayer


def _convertXmLSystem(xmlHarbieSystem):
	systemKey = xmlHarbieSystem.get("key")
	systemType = xmlHarbieSystem.get("type")
	if systemType not in HARBIE_TYPES:
		print "Unknow type", systemKey, systemType
		return None

	xmlHarbieParameters = xmlHarbieSystem.find("Parameters")
	settings = json.loads(xmlHarbieParameters.get("value", {}))

	if settings["location"] == "X":
		settings["location"] = "M"
		systemKey = systemKey.replace("_X", "_M")

	xmlSystem = etree.Element("System")
	xmlSystem.set("key", systemKey)
	xmlSystem.set("type", HARBIE_TYPES[systemType])

	connectionType = settings.pop("connectionType")
	connectionData = settings.pop("connections")
	xmlSystem.set("settings", json.dumps(settings))

	xmlConnections = _convertXmlConnection(connectionType, connectionData, systemType)
	xmlSystem.extend(xmlConnections)

	xmlHarbieMarkers = xmlHarbieSystem.find("Markers")
	for xmlHarbieMarker in xmlHarbieMarkers:
		name = xmlHarbieMarker.get("name")
		if "Crv" in name:
			continue
		xmlMarker = _convertXmlMarker(xmlHarbieMarker, systemType)
		xmlSystem.append(xmlMarker)

	return xmlSystem


def _convertXmlConnection(connectionType, connectionData, systemType):
	xmlConnections = []
	if connectionType == "standard":
		rotationTracker = {}
		for port, data in connectionData.iteritems():
			if "keyslots" not in data or not data["keyslots"]:
				continue

			if port == "UI":
				xmlConnection = _convertXmlConnectionUI(port, data)
				xmlConnections.append(xmlConnection)
			elif systemType in ["transformDriven01", "slider01", "rotationalSlider01", "tracker01"]\
				and port in ["Reference", "Tracker"]:
				rotationTracker[port] = data["keyslots"][0]
			else:
				xmlConnection = _convertXmlConnectionStandard(port, data)
				xmlConnections.append(xmlConnection)

		if rotationTracker:
			xmlConnection = _convertXmlConnectionRotationTracker(rotationTracker)
			xmlConnections.append(xmlConnection)

	elif connectionType == "obj2cls":
		for port, data in connectionData.iteritems():
			if "geometry" not in data or not data["geometry"]:
				continue

			xmlConnection = _convertXmlConnectionObj2Cls(port, data)
			xmlConnections.append(xmlConnection)

	return xmlConnections


def _convertXmlConnectionUI(port, data):
	keyslots = data["keyslots"]
	key, slot = keyslots[0]
	settings = dict(
		key=key,
		slot=slot)

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", port)
	xmlConnection.set("type", "uiHost")
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection


def _convertXmlConnectionStandard(port, data):
	keyslots = data["keyslots"]
	if len(keyslots) == 1:
		cnxType = "slotParent"
		key, slot = keyslots[0]

		settings = dict(
				key=key,
				slot=slot)
	else:
		cnxType = "multiParent"

		definitions = []
		for key, slot in keyslots:
			definition = dict(
				type="slot",
				key=key,
				slot=slot)
			definitions.append(definition)

		settings = dict(definitions=definitions)

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", port)
	xmlConnection.set("type", cnxType)
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection

def _convertXmlConnectionRotationTracker(data):
	refKey, refSlot = data["Reference"]
	trkKey, trkSlot = data["Tracker"]
	settings = dict(
		referenceKey=refKey,
		referenceSlot=refSlot,
		trackerKey=trkKey,
		trackerSlot=trkSlot)

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", "Tracker")
	xmlConnection.set("type", "rotationTracker")
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection

def _convertXmlConnectionObj2Cls(port, data):
	settings = dict(
		mesh=data["geometry"],
		componentType=COMPONENT_TYPES[data["clusterType"]],
		componentIndex=data["componentIndex"],
		key=data["oriReference"][0],
		slot=data["oriReference"][1],
		useOrientation=data["useClusterOrientation"],
		useClosest=data["componentIndex"] == "" or data["componentIndex"] is None
	)

	xmlConnection = etree.Element("Connection")
	xmlConnection.set("port", port)
	xmlConnection.set("type", "meshAttach")
	xmlConnection.set("settings", json.dumps(settings))

	return xmlConnection



def _convertXmlMarker(xmlHarbieMarker, systemType):
	xmlMarker = etree.Element("Marker")
	name = xmlHarbieMarker.get("name")

	if systemType in MARKER_NAMES and name in MARKER_NAMES[systemType]:
		name = MARKER_NAMES[systemType][name]

	xmlMarker.set("name", name)

	# Transform
	transform = json.loads(xmlHarbieMarker.get("transform"))
	matrix = _convertTransformToMatrix(**transform)
	xmlMarker.set("matrix", json.dumps(list(matrix)))

	return xmlMarker


def _convertTransformToMatrix(translation, rotation, scaling):
	rotation = rotation[1:] + rotation[:1]

	translation = Vector3(translation)
	rotation = Quaternion(rotation)
	scaling = Vector3(scaling)

	transform = Transformation.fromParts(translation, rotation, scaling)
	return transform.asMatrix().flattened()
