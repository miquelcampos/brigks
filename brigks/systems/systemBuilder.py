from collections import OrderedDict
import itertools

from maya import cmds
from tools.marbie.core import naming 


class SystemBuilder():

	def __init__(self, coreBuilder, guide):
		self.coreBuilder = coreBuilder
		self.guide = guide
		self.key = self.guide.key
		self.settings = self.guide.settings

		# Building Steps
		# For each system we're building, each step will be processed for all the systems
		# before running the next step. This ensure all the objects have been created 
		# before we start connecting systems together.
		self.steps = OrderedDict()
		self.steps["Clean System"] = self.delete
		self.steps["Create Objects"] = self.createObjects
		self.steps["Create Operators"] = self.createOperator
		self.steps["Create Attributes"] = self.createAttributes
		self.steps["Connect System"] = self.connect

	# ----------------------------------------------------------------------------------
	# BUILDING STEPS
	# ----------------------------------------------------------------------------------
	def delete(self):
		search = self.getObject("*", "*")
		parent = cmds.ls(self.coreBuilder.localCtl, long=True)[0]
		toDelete = [x for x in cmds.ls(search, type="transform", long=True) if x.startswith(parent)]
		if toDelete:

			# Unparent all the children
			children = cmds.listRelatives(toDelete, children=True, path=True)
			children = [x for x in cmds.ls(children, long=True) if x not in toDelete]
			if children:
				cmds.parent(children, self.coreBuilder.localCtl)

			# Delete objects
			cmds.delete(toDelete)

	def createObjects(self):
		pass

	def createOperator(self):
		pass

	def createAttributes(self):
		pass

	def connect(self):
		for slot, cnx in self.guide.connections.iteritems():
			cnx.connect(self, slot)

	# ----------------------------------------------------------------------------------
	#  OBJECTS
	# ----------------------------------------------------------------------------------
	def createTransform(self, parent, part, usage, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		parent = parent if parent is not None else self.coreBuilder.localCtl
		name = self.getObjectName(usage, part)

		node = cmds.createNode("transform", name=name)
		cmds.parent(node, parent)

		# Transform
		matrix = [list(x) for x in tfm.getMatrix4()]
		flatten = list(itertools.chain(*matrix))
		cmds.xform(node, matrix=flatten)

		return node

	def createController(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		usage = "Ctl"
		return self.createTransform(parent, part, usage, tfm, icon, size, po, ro, so, color)

	def createBuffer(self, parent, part, tfm=None):
		usage = "Bfr"
		icon = "cube"
		size = .2
		color = [0,0,0]
		return self.createTransform(parent, part, usage, tfm, icon, size, color=color)

	def createJoint(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		usage = "Jnt"
		color = [1,0,0]
		return self.createTransform(parent, part, usage, tfm, icon, size, po, ro, so, color=color)

	def createRig(self, parent, part, tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None):
		usage = "Rig"
		color = [0,0,0]
		return self.createTransform(parent, part, usage, tfm, icon, size, po, ro, so, color)

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def getObjectName(self, usage, part):
		return naming.getObjectName(
			usage=usage,
			location=self.settings["location"],
			name=self.settings["name"],
			part=part)

	def getObject(self, usage, part):
		return self.getObjectName(usage, part)

	def getObjectFromSlot(self, slot):
		slots = self.guide.connectionSlots()
		if slot in slots:
			usage, part = slots[slot]
			return self.getObject(usage, part)

