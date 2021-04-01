import json
import xml.etree.cElementTree as etree
from maya import cmds
import dcc.maya.compound


class SystemConnection(object):

	def __init__(self):
		self.settings = dict()

	def dumps(self):
		return dict(type=self.type(),
					settings=self.settings)

	def type(self):
		return self.__module__.split(".")[-2]

	def setConnection(self, settings):
		self.settings.update(settings)

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
		xmlRoot.set("settings", json.dumps(self.settings))
		return xmlRoot

	@classmethod
	def fromXml(cls, xmlRoot):
		connection = cls()

		# Load Settings
		settings = json.loads(xmlRoot.get("settings", {}))
		connection.settings.update(settings)

		return connection
