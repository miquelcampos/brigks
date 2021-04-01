
import os.path
import sys
from dcc.maya.decorators import mayacommand
import xml.etree.cElementTree as etree
import json

from Qt.QtWidgets import QDialog, QVBoxLayout, QPushButton, QApplication

from tools.marbie import Guide, Builder
from tools.marbie.gui.guideTreeWidget import GuideTreeWidget
from tools.marbie.gui.systemSettingsWidget import SystemSettingsWidget
from tools.marbie.utils.convert import convertXmlHarbie

hierarchyXMLPath = os.path.join(os.path.dirname(__file__),"hierarchy_SplitDoubled.xml")


# TODOS
# - Implement systemMarker to manipulate shapes and transforms
# - Build a simple biped (Arms, Basics)
# - System Type updated (chain with Arm or Basic)
# - Implement second type of Connection (Mutli Cns) and Swap Connection Type
# - How to detect Systems that are connected? to recreate those connection. Including Attributes


# @mayacommand()
# def createGuide():
# 	guide = Guide()

# 	xmlHierarchy = etree.parse(hierarchyXMLPath).getroot()
# 	for xmlNode in xmlHierarchy:
# 		_createGuideFromXml(xmlNode, parent=guide)

# 	guide.dumps()
# 	return guide

# def _createGuideFromXml(xmlNode, parent):
# 	if xmlNode.tag == "layer":
# 		name = xmlNode.get("name")
# 		layer = parent.addLayer(name)

# 		for xmlChild in xmlNode:
# 			_createGuideFromXml(xmlChild, layer)

# 	elif xmlNode.tag == "system":
# 		name = xmlNode.get("name")
# 		location = xmlNode.get("location")
# 		type_ = xmlNode.get("type")
# 		system = parent.addSystem(systemType=type_, location=location, name=name)

# 		for xmlChild in xmlNode:
# 			_createGuideFromXml(xmlChild, system)

# 	elif xmlNode.tag == "connection":
# 		type_ = xmlNode.get("type")
# 		port = xmlNode.get("port")
# 		data = json.loads(xmlNode.get("settings"))
# 		cnx = parent.addConnection(connectionType=type_, port=port)
# 		cnx.setConnection(data)

@mayacommand()
def loadGuide():
	guide = Guide(model="Guide")
	return guide

@mayacommand()
def guideDumps(guide):
	guide.dumps()

@mayacommand()
def guideToXml(guide, path):
	xmlRoot = guide.toXml()
	indent(xmlRoot)
	tree = etree.ElementTree(xmlRoot)
	tree.write(path)



@mayacommand()
def guideFromXml(path):
	return Guide.fromXml(path)

@mayacommand()
def build(guide):
	builder = Builder(guide)

	layer = guide.layers.values()[0]
	builder.build(layer.systems.values())
	return builder

@mayacommand()
def showGuideTree(guide):
	dialog = QDialog()
	layout = QVBoxLayout()
	uiTreeWDG = GuideTreeWidget(guide)
	layout.addWidget(uiTreeWDG)

	uiBuildBTN = QPushButton("Build")
	uiBuildBTN.clicked.connect(dialog.accept)
	layout.addWidget(uiBuildBTN)

	uSettingsBTN = QPushButton("Settings")
	uSettingsBTN.clicked.connect(lambda:showSystemSettingsWidget(uiTreeWDG))
	layout.addWidget(uSettingsBTN)
	dialog.setLayout(layout)


	if not dialog.exec_():
		return

	systems = uiTreeWDG.selectedSystems()

	builder = Builder(guide)

	builder.build(systems)

@mayacommand()
def showSystemSettingsWidget(tree):

	system = tree.selectedSystems()[0]

	dialog = QDialog()
	layout = QVBoxLayout()
	uiTreeWDG = SystemSettingsWidget(system)
	layout.addWidget(uiTreeWDG)

	dialog.setLayout(layout)

	if not dialog.exec_():
		return


@mayacommand()
def showWindow():
	from tools.marbie.gui.marbieWindow import MarbieWindow
	window = MarbieWindow()

	window.exec_()


@mayacommand()
def showSystemSettings(system):
	from tools.marbie.gui.systemSettingsWidget import SystemSettingsWidget
	widget = SystemSettingsWidget(system)

	dialog = QDialog()
	layout = QVBoxLayout()
	layout.addWidget(widget)
	dialog.setLayout(layout)

	if not dialog.exec_():
		return



def fromHarbie():
	path = r"K:\Departments\Rigging\Prefab\Harbie\Templates\biped_AllXML.xml"
	outputPath = r"\\source\source\dev\passerin\tools\tools\marbie\tests\harbieFullBiped.xml"

	xmlHarbie = etree.parse(path).getroot()
	xmlRoot = convertXmlHarbie(xmlHarbie)

	indent(xmlRoot)
	tree = etree.ElementTree(xmlRoot)
	tree.write(outputPath)

	print "Exported to", outputPath


# # Add Connections
# allKeys = []

# for layer in guide.layers.values():
# 	allKeys.extend(layer.systems.keys())
# 	for sublayer in layer.layers.values():
# 		allKeys.extend(sublayer.systems.keys())
	

# for layer in guide.layers.values():
# 	for system in layer.systems.values():
# 		cnx = system.addConnection("parent", "Test")
# 		key = random.choice(allKeys)
# 		cnx.setConnection(dict(otherKey=key, otherSlot="Test"))
# 		cnx = system.addConnection("parent", "Test2")
# 		key = random.choice(allKeys)
# 		cnx.setConnection(dict(otherKey=key, otherSlot="Test"))
# 		cnx = system.addConnection("parent", "Test3")
# 		key = random.choice(allKeys)
# 		cnx.setConnection(dict(otherKey=key, otherSlot="Test"))




# for layer in guide.layers.values():
# 	for system in layer.systems.values():
# 		cnx = system.addConnection("parent", "Part2")
# 		cnx.setConnection(dict(otherKey=system.key(), otherSlot="Part1"))
# 		cnx = system.addConnection("parent", "Part3")
# 		cnx.setConnection(dict(otherKey=system.key(), otherSlot="Part2"))
		
# 	for sublayer in layer.layers.values():
# 		for system in sublayer.systems.values():
# 			cnx = system.addConnection("parent", "Part2")
# 			cnx.setConnection(dict(otherKey=system.key(), otherSlot="Part1"))
# 			cnx = system.addConnection("parent", "Part3")
# 			cnx.setConnection(dict(otherKey=system.key(), otherSlot="Part2"))



# --------------------------------------------------------------------------------------
# MISC
# --------------------------------------------------------------------------------------

def indent(elem, level=0):
	i = "\n" + level*" "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + " "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i