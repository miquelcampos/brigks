import json
import xml.etree.cElementTree as etree
from maya import cmds

from brigks.utils import compounds

class SystemConnection(object):

	def __init__(self):
		self._settings = dict()
		self._builder = None

	def dumps(self):
		return dict(type=self.type(),
					settings=self._settings)

	def type(self):
		return self.__module__.split(".")[-2]

	def setBuilder(self, builder):
		self._builder = builder
		self.getObjectName = self._builder.getObjectName

	def setSettings(self, **settings):
		self._settings.update(settings)

	def settings(self, key=None):
		return self._settings if key is None else self._settings[key]

	# ----------------------------------------------------------------------------------
	# REIMPLEMENT
	# ----------------------------------------------------------------------------------
	def connect(self):
		pass

	def getTargetSystems(self):
		return []

	def splitSymmetry(self, location):
		pass

	# ----------------------------------------------------------------------------------
	# 
	# ----------------------------------------------------------------------------------
	def getParentFromSlot(self, key, slot):
		parent = None
		if key in self._builder.coreBuilder.systems:
			system = self._builder.coreBuilder.systems[key]
			parent = system.getObjectFromSlot(slot)
		if parent is None:
			parent = self._builder.coreBuilder.localCtl
		return parent

	def getParentFromMesh(self, mesh, useClosest, useOrientation, componentType, componentIndex, key, slot, position):
		parent = self.getParentFromSlot(key, slot)

		attachName = self.getObjectName(usage="Rig", part="MeshAttach")
		attach = cmds.createNode("transform", name=attachName)
		cmds.parent(attach, parent)
		cmds.xform(attach, translation=position, worldSpace=True)

		compounds.meshMultiAttach(attach, mesh, componentType, componentIndex, useOrientation)
		return attach

	def getParentFromSurface(self, surface, useClosest, u, v, key, slot, position):
		parent = self.getParentFromSlot(key, slot)

		if useClosest:
			u, v = None, None

		attachName = self.getObjectName(usage="Rig", part="MeshAttach")
		attach = cmds.createNode("transform", name=attachName)
		cmds.parent(attach, parent)
		cmds.xform(attach, translation=position, worldSpace=True)

		compounds.surfaceAttach(attach, surface, u, v)
		return attach

	def getParentFromName(self, name):
		model = self._builder.coreBuilder.model()
		for name in [cmds.ls(name, long=True)]:
			if name.startswith(model):
				return name

	# ----------------------------------------------------------------------------------
	# CONNECTION HELPERS
	# ----------------------------------------------------------------------------------
	def _parent(self, child, parent):
		if not parent:
			return

		# Making sure the object is not already a child of the parent
		# Otherwise Maya throws an error
		if child in (cmds.listRelatives(parent, children=True) or []):
			return

		cmds.parent(child, parent)

	def _parentConstraint(self, slave, masters):
		name = "MultiParent"
		return compounds.blendMatrix(slave, masters, maintainOffset=True)

	# ----------------------------------------------------------------------------------
	# XML IO
	# ----------------------------------------------------------------------------------
	def toXml(self, port):
		xmlRoot = etree.Element("Connection")
		xmlRoot.set("type", self.type())
		xmlRoot.set("port", port)
		xmlRoot.set("settings", json.dumps(self._settings))
		return xmlRoot

	@classmethod
	def fromXml(cls, xmlRoot):
		connection = cls()

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", {}))
		connection.setSettings(**settings)

		return connection
