import json
import xml.etree.cElementTree as etree
from maya import cmds
import dcc.maya.compound


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

	def setSettings(self, settings):
		self._settings.update(settings)

	def settings(self):
		return self._settings

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
		dcc.maya.compound.create("PoseConstraint2", name, slave, masters, compensation=True)

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
		connection.setSettings(settings)

		return connection
