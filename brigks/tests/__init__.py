
import os.path
import sys
import json
import sip
import xml.etree.cElementTree as etree
from Qt.QtWidgets import QDialog, QVBoxLayout, QPushButton, QApplication, QWidget

from dcc.maya.decorators import mayacommand

import maya.OpenMayaUI as mui

from brigks import Guide, Builder
from brigks.gui.guideTreeWidget import GuideTreeWidget
from brigks.gui.systemSettingsWidget import SystemSettingsWidget
from brigks.utils.xml import indent

from math3d.transformation import Transformation
from math3d.vectorN import Vector3



# TODOS
# - Implement systemMarker to manipulate shapes and transforms
# - Build a simple biped (Arms, Basics)
# - System Type updated (chain with Arm or Basic)
# - Implement second type of Connection (Mutli Cns) and Swap Connection Type
# - How to detect Systems that are connected? to recreate those connection. Including Attributes



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


def createSimpleGuideAndBuild():
	from brigks.gui import showWindow
	from brigks import Guide
	from math3d.transformation import Transformation
	from math3d.vectorN import Vector3

	# Building Matrix for guide positions
	basicMatrices = {}
	chainMatrices = {}
	for i in range(4):
		x = 3 if i == 2 else i
		t = Transformation.fromParts(translation=Vector3([x,i,0]))
		basicMatrices["Part%s"%(i+1)] = t.asMatrix().flattened()

		t = Transformation.fromParts(translation=Vector3([x,i,2]))
		chainMatrices["Bone%s"%(i+1)] = t.asMatrix().flattened()

	# Create Guide, add a layer and a couple Systems
	g = Guide()
	layer = g.addLayer("MyFirstLayer")
	basic = layer.addSystem("basic", "L", "Basic", basicMatrices)
	chain = layer.addSystem("chain", "L", "Chain", chainMatrices)

	# System Settings
	basic.setSettings(dynamic=True, dynamicAnimatable=True, splitRotation=True)
	chain.setSettings(dynamic=True, dynamicAnimatable=True, kinematics="FK/IK", strap=True)

	# Add Pre/Pest Script to System
	basic.setSettings(preScriptValue="print 'hello system', this_model")
	basic.setSettings(postScriptValue="print 'bye system', this_guide")

	# System Connections
	cnx = basic.addConnection("multiParent", "Part2")
	cnx.setSettings(definitions=[
		dict(type="slot",key="Basic_L", slot="Part1"),
		dict(type="slot",key="Basic_L", slot="Part3"),
		dict(type="slot",key="Basic_L", slot="Part4")
	])

	cnx = chain.addConnection("slotParent", "Root")
	cnx.setSettings(key="Basic_L", slot="Part1")

	# Add Pre/Post Script to Guide
	#g.setSettings(preScriptValue="print 'hello', this_model")
	#g.setSettings(postScriptValue="print 'bye', this_guide")

	# Save edit
	g.commit()

	# Build all rig
	g.build()

	showWindow()





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
def showSystemSettings(system):
	from brigks.gui.systemSettingsWidget import SystemSettingsWidget
	widget = SystemSettingsWidget(system)

	dialog = QDialog()
	layout = QVBoxLayout()
	layout.addWidget(widget)
	dialog.setLayout(layout)

	if not dialog.exec_():
		return



def fromHarbie():
	from brigks.utils.convert import convertXmlHarbie
	# Convert the Harbie template to Brigks
	path = r"K:\Departments\Rigging\Prefab\Harbie\Templates\biped_AllXML.xml"
	outputPath = r"\\source\source\dev\passerin\brigks\brigks\tests\harbieFullBiped.xml"

	xmlHarbie = etree.parse(path).getroot()
	xmlRoot = convertXmlHarbie(xmlHarbie)

	indent(xmlRoot)
	tree = etree.ElementTree(xmlRoot)
	tree.write(outputPath)

	print "Exported to", outputPath
