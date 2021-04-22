import os.path
import xml.etree.cElementTree as etree
from datetime import datetime as dt
import logging

from Qt.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView
from Qt.QtGui import QBrush, QColor
from Qt import QtCompat
from Qt.QtCore import Qt

from brigks import Guide
from brigks.gui.systemSettingsWidget import SystemSettingsWidget
from brigks.utils import context, xmldom
from brigks.gui import showWindow

from math3d.transformation import Transformation
from math3d.vectorN import Vector3
from math3d.euler import Euler


# TODOS
# - Implement systemMarker to manipulate shapes and transforms
# - Build a simple biped (Arms, Basics)

@context.command()
def guideToXml(guide, path):
	xmlRoot = guide.toXml()
	xmldom.indent(xmlRoot)
	tree = etree.ElementTree(xmlRoot)
	tree.write(path)


def createSimpleGuideAndBuild(showWindow=False):
	# Building Matrix for guide positions
	basicMatrices = {}
	chainMatrices = {}
	for i in range(4):
		x = 3 if i == 2 else i
		t = Transformation.fromParts(translation=Vector3([x,i,0]))
		basicMatrices["Part%s"%(i+1)] = t.asMatrix().flattened()

		t = Transformation.fromParts(translation=Vector3([x,i,2]))
		chainMatrices["Part%s"%(i+1)] = t.asMatrix().flattened()

	# Create Guide, add a layer and a couple Systems
	g = Guide()
	layer = g.addLayer("MyFirstLayer")
	basic = layer.addSystem("basic", "L", "Basic", basicMatrices)
	chain = layer.addSystem("chain", "L", "Chain", chainMatrices)

	# System Settings
	#basic.setSettings(dynamic=True, dynamicAnimatable=True, splitRotation=True)
	chain.setSettings(dynamic=True, dynamicAnimatable=True, kinematic="FK/IK", strap=True)

	# Add Pre/Pest Script to System
	# basic.setSettings(preScriptValue="print 'This is a Pre Script for the system {k}'.format(k=this_guide.key())")
	# basic.setSettings(postScriptValue="print 'This is a Post Script for the system {k}'.format(k=this_guide.key())")

	# System Connections
	cnx = basic.addConnection("UI", connectionType="uiHost")
	cnx.setSettings(key="Basic_L", slot="Part1")

	cnx = basic.addConnection("Part2", connectionType="multiParent")
	cnx.setSettings(definitions=[
		dict(type="slot",key="Basic_L", slot="Part1"),
		dict(type="slot",key="Basic_L", slot="Part3"),
		dict(type="slot",key="Basic_L", slot="Part4")
	])

	cnx = chain.addConnection("UI", connectionType="uiHost")
	cnx.setSettings(key="Basic_L", slot="Part1")

	# cnx = chain.addConnection("Root", connectionType="slotParent")
	# cnx.setSettings(key="Basic_L", slot="Part1")

	# Add Pre/Post Script to Guide
	# g.setSettings(preScriptValue="print 'This is a Pre Global Script for the guide {g}'.format(g=this_guide)")
	# g.setSettings(postScriptValue="print 'This is a Post Global Script for the model {m}'.format(m=this_model)")

	# Save edit
	g.commit()

	# Build all rig
	g.build()

	if showWindow:
		showWindow()

	return g

def rebuild(showWindow=False):
	g = createSimpleGuideAndBuild(showWindow=False)

	basic = g.findSystem("Basic_L")
	chain = g.findSystem("Chain_L")

	# Change settings and rebuild
	# cnx = chain.connections("UI")
	# cnx.setSettings(key="Basic_L", slot="Part2")
	# g.commit()

	# Build all rig
	basic.build()
	# chain.build()

	if showWindow:
		showWindow()


def deleteGuides(deleteGuide=False, showWindow=False):
	g = createSimpleGuideAndBuild(showWindow=False)

	basic = g.findSystem("Basic_L")
	chain = g.findSystem("Chain_L")

	basic.delete(deleteGuide)
	chain.delete(deleteGuide)

	if showWindow:
		showWindow()



def createGuideDuplicateAndBuild(showWindow=False):
	# Building Matrix for guide positions
	basicMatrices = {}
	chainMatrices = {}

	basicMatrices = dict(
		Part1=Transformation.fromParts(translation=Vector3([1,0,-1]), rotation=Euler([0,25,25], degrees=True).asQuaternion()),
		Part2=Transformation.fromParts(translation=Vector3([1,1,-1]), rotation=Euler([0,25,25], degrees=True).asQuaternion()),
		Part3=Transformation.fromParts(translation=Vector3([2,1,-1]), rotation=Euler([0,25,25], degrees=True).asQuaternion())
		)
	chainMatrices = dict(
		Part1=Transformation.fromParts(translation=Vector3([1,0,4])),
		Part2=Transformation.fromParts(translation=Vector3([1,1,4])),
		Part3=Transformation.fromParts(translation=Vector3([2,1,4])),
		Part4=Transformation.fromParts(translation=Vector3([2,2,4]))
		)

	# Create Guide, add a layer and a couple Systems
	g = Guide()
	g.setSettings(hideRig=False)
	# g.setSettings(stopAfter="Create Objects")

	layer = g.addLayer("MyFirstLayer")

	basicL = layer.addSystem("basic", "X", "Basic", basicMatrices)
	basicL.setSettings(dynamic=True, dynamicAnimatable=True, splitRotation=True)

	chainL = layer.addSystem("chain", "X", "Chain", chainMatrices)
	chainL.setSettings(dynamic=True, dynamicAnimatable=True, kinematic="FK/IK", strap=True)

	# basicR = basicL.duplicate(mirror=True)
	# chainR = chainL.duplicate(mirror=True)

	# This is how you split a X guide 
	basicL.rename(location="L", name=basicL.settings("name"))
	basicR = basicL.duplicate(mirror=True)
	chainL.rename(location="L", name=chainL.settings("name"))
	chainR = chainL.duplicate(mirror=True)


	# Save edit
	g.commit()

	# Build all rig
	g.build()

	if showWindow:
		showWindow()

	return g




def createGuidesAndBuild(location="M", mirror=False, showWindow=False):
	# Building Matrix for guide positions

	# Create Guide, add a layer and a couple Systems
	g = Guide()
	g.setSettings(hideRig=False)
	g.setSettings(hideJoints=False)
	# g.setSettings(stopAfter="Create Objects")

	layer = g.addLayer("MyFirstLayer")
	# basicA = layer.addSystem("basic", location, "BasicA")
	# basicB = layer.addSystem("basic", location, "BasicB")
	# chain = layer.addSystem("chain", location, "Chain")
	# stretch = layer.addSystem("stretch", location, "Stretch")
	# slider = layer.addSystem("slider", location, "Slider")
	# twist = layer.addSystem("twist", location, "Twist")
	# spine = layer.addSystem("spine", location, "Spine")
	# arm = layer.addSystem("arm", location, "Arm")
	leg = layer.addSystem("leg", location, "Leg")
	# neck = layer.addSystem("neck", location, "Neck")
	# average = layer.addSystem("average", location, "Average")
	# breast = layer.addSystem("breast", location, "Breast")
	# camera = layer.addSystem("camera", location, "Camera")
	# driven = layer.addSystem("driven", location, "Driven")
	# foot = layer.addSystem("foot", location, "Foot")
	# lookat = layer.addSystem("lookat", location, "LookAt")
	# meta = layer.addSystem("meta", location, "Meta")
	# piston = layer.addSystem("piston", location, "Piston")
	# quadrant = layer.addSystem("quadrant", location, "Quadrant")
	# tracker = layer.addSystem("tracker", location, "Tracker")
	# attribute = layer.addSystem("attribute", location, "Attribute")
	# zleg = layer.addSystem("zleg", location, "ZLeg")
	# psd = layer.addSystem("psd", location, "PSD")
	# tentacle = layer.addSystem("tentacle", location, "Tentacle")

	# System Settings
	# slider.setSettings(dynamic=True, dynamicAnimatable=True, splitRotation=True)
	# stretch.setSettings(squash=True)

	# Connections
	# slider.addConnection("Tracker", "rotationTracker", 
	# 		referenceKey="BasicA_{}".format(location),
	# 		referenceSlot="Part1",
	# 		trackerKey="BasicB_{}".format(location),
	# 		trackerSlot="Part1",)

	if location != "X" and mirror:
		for system in layer.systems():
			system.duplicate(mirror=True)

	# Save edit
	g.commit()

	# Build all rig
	g.build()

	if showWindow:
		showWindow()

	return g


@context.command()
def showSystemSettings(system):
	from brigks.gui.systemSettingsWidget import SystemSettingsWidget
	widget = SystemSettingsWidget(system)

	dialog = QDialog()
	layout = QVBoxLayout()
	layout.addWidget(widget)
	dialog.setLayout(layout)

	if not dialog.exec_():
		return

def DDTree():


	tree = TreeWidget()

	dialog = QDialog()
	layout = QVBoxLayout()
	layout.addWidget(tree)
	dialog.setLayout(layout)

	if not dialog.exec_():
		return

class TreeWidget(QTreeWidget):

	def __init__(self, guide=None):
		super(TreeWidget, self).__init__()

		self.setColumnCount(1)
		self.setSelectionMode(self.ExtendedSelection)
		self.setDragDropMode(self.DragDrop)
		self.setDefaultDropAction(Qt.MoveAction)
		self.setHeaderHidden(True)
		
		for i in range(3):
			item = QTreeWidgetItem(self, ["LAYER LAYER {}".format(i)])
			for i in range(3):
				QTreeWidgetItem(self, ["SYSTEM SYSTEM {}".format(i)])
			
		self.itemSelectionChanged.connect(self.allowDragNDrop)

	def allowDragNDrop(self):
		items = self.selectedItems()
		if not items:
			return 

		if items[0].text(0).startswith("SYSTEM"):
			self.setDragDropMode(self.NoDragDrop)
		else:
			self.setDragDropMode(self.DragDrop)



@context.command()
def fromHarbie():
	from brigks.utils.convert import convertXmlHarbie
	# Convert the Harbie template to Brigks
	path = r"K:\Departments\Rigging\Prefab\Harbie\Templates\biped_AllXML.xml"
	outputFPath = r"\\source\source\dev\passerin\brigks\brigks\tests\harbieFullBiped.xml"
	outputXPath = r"\\source\source\dev\passerin\brigks\brigks\tests\harbieXBiped.xml"

	start = dt.now()

	xmlHarbie = etree.parse(path).getroot()
	xmlRoot = convertXmlHarbie(xmlHarbie, useSymmetrySystems=False)
	xmldom.indent(xmlRoot)
	tree = etree.ElementTree(xmlRoot)
	tree.write(outputFPath)

	logging.info("Conversion Full {t}".format(t=(dt.now() - start)))
	start = dt.now()

	xmlRoot = convertXmlHarbie(xmlHarbie, useSymmetrySystems=True)
	xmldom.indent(xmlRoot)
	tree = etree.ElementTree(xmlRoot)
	tree.write(outputXPath)

	logging.info("Conversion X {t}".format(t=(dt.now() - start)))
	start = dt.now()

	guide = Guide.fromXml(outputFPath)

	logging.info("Guide Creation {t}".format(t=(dt.now() - start)))

	logging.info("Exported to {p}".format(p=outputFPath))
	logging.info("Exported to {p}".format(p=outputXPath))

	return guide

def reloadModule():
	import os, sys
	path = r'\\source\source\dev\passerin\brigks'
	path = os.path.normcase(os.path.normpath(path))
	if sys.path[0] != path:
		sys.path.insert(0, path)

	for key, value in sys.modules.items():
		try:
			packPath = value.__file__
		except AttributeError:
			continue

		packPath = os.path.normcase(os.path.normpath(packPath))
		if packPath.startswith(path):
			sys.modules.pop(key)

def loggingFormatter():
	import logging
	import sys

	sh = logging.StreamHandler(stream=sys.stdout)
	fmt = logging.Formatter("%(levelname)s: %(message)s")
	sh.setFormatter(fmt)

	logging.root.handlers = []
	logging.root.addHandler(sh)

	logging.info("Hello Info")
	logging.warning("Hello Warning")