

from brigks import Guide
from brigks.gui import showWindow

from math3d import Transformation, Vector3


def exampleA(mirror=False, showWindow=False):
	'''Built a basic and a chain system. Set the basic to be dynamic and connect the chain to it.
	
	Args:
		mirror (bool): True to duplicate the systems on the right side
		showWindow (bool): True to popup Brigks Main Window
	'''
	# Building Matrix for guide positions
	basicMatrices = {}
	chainMatrices = {}
	for i in range(4):
		x = 3 if i == 2 else i
		t = Transformation.fromParts(translation=Vector3([x,i,0]))
		basicMatrices["Part{}".format(i+1)] = t.asMatrix().flattened()

		t = Transformation.fromParts(translation=Vector3([x,i,2]))
		chainMatrices["Part{}".format(i+1)] = t.asMatrix().flattened()

	# Create Guide, add a layer and a couple Systems
	guide = Guide()
	guide.setSettings(hideRig=False)
	guide.setSettings(hideJoints=False)

	layer = guide.addLayer("MyFirstLayer")
	basic = layer.addSystem("basic", "L", "Basic", basicMatrices)
	chain = layer.addSystem("chain", "L", "Chain", chainMatrices)

	# System Settings
	basic.setSettings(dynamic=True, dynamicAnimatable=True, strap=True)

	# Connections
	chain.addConnection("Root", "slotParent", 
			key=basic.key(),
			slot="Part1")

	if mirror:
		for system in layer.systems().values():
			system.duplicate(mirror=True)

	# Save edit
	guide.commit()

	# Build all rig
	guide.build()

	if showWindow:
		showWindow()

	return guide