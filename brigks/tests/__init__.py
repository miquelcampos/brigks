
import os.path
import xml.etree.cElementTree as etree
from datetime import datetime as dt
from Qt.QtWidgets import QDialog, QVBoxLayout

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
		Part1=Transformation.fromParts(translation=Vector3([1,0,0]), rotation=Euler([0,25,25], degrees=True).asQuaternion()),
		Part2=Transformation.fromParts(translation=Vector3([1,1,0]), rotation=Euler([0,25,25], degrees=True).asQuaternion()),
		Part3=Transformation.fromParts(translation=Vector3([2,1,0]), rotation=Euler([0,25,25], degrees=True).asQuaternion())
		)
	chainMatrices = dict(
		Part1=Transformation.fromParts(translation=Vector3([1,0,3])),
		Part2=Transformation.fromParts(translation=Vector3([1,1,3])),
		Part3=Transformation.fromParts(translation=Vector3([2,1,3])),
		Part4=Transformation.fromParts(translation=Vector3([2,2,3]))
		)

	# Create Guide, add a layer and a couple Systems
	g = Guide()
	layer = g.addLayer("MyFirstLayer")
	g.setSettings(stopAfter="Create Objects")

	basicL = layer.addSystem("basic", "L", "Basic", basicMatrices)
	#basic1 = basicL.duplicate()
	basicR = basicL.duplicate(mirror=True)
	chainL = layer.addSystem("chain", "L", "Chain", chainMatrices)
	chainR = chainL.duplicate(mirror=True)

	# System Settings
	#basic.setSettings(dynamic=True, dynamicAnimatable=True, splitRotation=True)
	#chain.setSettings(dynamic=True, dynamicAnimatable=True, kinematic="FK/IK", strap=True)

	# Save edit
	g.commit()

	# Build all rig
	#g.build()

	if showWindow:
		showWindow()

	return g

def createXGuideAndBuild(showWindow=False):
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
	g.setSettings(stopAfter="Create Objects")

	#basic = layer.addSystem("basic", "L", "Basic", basicMatrices)
	#chain = layer.addSystem("chain", "L", "Chain", chainMatrices)

	# System Settings
	#basic.setSettings(dynamic=True, dynamicAnimatable=True, splitRotation=True)
	#chain.setSettings(dynamic=True, dynamicAnimatable=True, kinematic="FK/IK", strap=True)

	# Save edit
	g.commit()

	# Build all rig
	g.build()

	if showWindow:
		showWindow()

	return g



def createStretchSliderGuideAndBuild(showWindow=False):
	# Building Matrix for guide positions
	sliderMatrices = dict(
		Rail1=Transformation.fromParts(translation=Vector3([0,0,0])),
		Pos1=Transformation.fromParts(translation=Vector3([1,0,0])),
		Neg1=Transformation.fromParts(translation=Vector3([-1,0,0]))
		)
	stretchMatrices = dict(
		Root=Transformation.fromParts(translation=Vector3([0,3,0])),
		End=Transformation.fromParts(translation=Vector3([2,3,0]))
		)

	# Create Guide, add a layer and a couple Systems
	g = Guide()
	layer = g.addLayer("MyFirstLayer")
	slider = layer.addSystem("slider", "L", "Basic", sliderMatrices)
	stretch = layer.addSystem("stretch", "L", "Chain", stretchMatrices)

	# System Settings
	#slider.setSettings(dynamic=True, dynamicAnimatable=True, splitRotation=True)
	stretch.setSettings(squash=True)


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

	print "conversion Full", dt.now() - start
	start = dt.now()

	xmlRoot = convertXmlHarbie(xmlHarbie, useSymmetrySystems=True)
	xmldom.indent(xmlRoot)
	tree = etree.ElementTree(xmlRoot)
	tree.write(outputXPath)

	print "conversion X", dt.now() - start
	start = dt.now()

	guide = Guide.fromXml(outputFPath)

	print "guide creation", dt.now() - start


	print "Exported to", outputFPath
	print "Exported to", outputXPath

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