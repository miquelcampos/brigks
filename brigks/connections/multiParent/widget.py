import os.path
from Qt import QtCompat

from tools.marbie.connections.systemConnectionWidget import SystemConnectionWidget


class MultiParentConnectionWidget(SystemConnectionWidget):

	def __init__(self, connection, system):
		super(MultiParentConnectionWidget, self).__init__(connection, system)
		uiPath = os.path.join(os.path.dirname(__file__), "widget.ui")
		QtCompat.loadUi(uiPath, self)

		self.uiAddBTN.clicked.connect(self.addParent)
		self.uiUpBTN.clicked.connect(lambda: self.move("up"))
		self.uiDownBTN.clicked.connect(lambda: self.move("down"))
		self.uiRemoveBTN.clicked.connect(self.removeParent)
		self.uiEditBTN.clicked.connect(self.editParent)
		self.uiDefaultCBOX.currentIndexChanged.connect(self.saveSettings)

	def loadSettings(self):
		self.self.uiParentsTREE.clear()
		items = []
		for definition in self.settings["definitions"]:
			cnxType = definition["type"]
			if cnxType == "slot":
				name = "{key}.{slot}".format(definition)
			elif cnxType == "custom":
				name = "{parent}".format(definition)
			elif cnxType == "mesh":
				name = "{mesh}.{componentType}[{componentIndex}] orient={useOrientation}".format(definition)
			elif cnxType == "nurbs":
				name = "{mesh}.[{u};{v}]".format(definition)

			self.uiParentsTREE.addTopLevelItem([name])
			items.append(name)

		default = self.settings["default"]
		self.uiDefaultCBOX.clear()
		self.uiDefaultCBOX.addItems(items)
		self.uiDefaultCBOX.setCurrentIndex(default)

	def saveSettings(self, definitions):
		definitions = definitions if definitions else self._connection.settings["definitions"]
		self._connection.settings["definitions"] = definitions
		self._connection.settings["default"] = self.uiDefaultCBOX.currentIndex()
		self._system.coreGuide.dumps()

	def addParent(self):
		pass

	def removeParent(self):
		index = self.uiParentsTREE.currentIndex()
		self._connection.settings["definitions"].pop(index)
		self._system.coreGuide.dumps()

		default = self._connection.settings["default"]
		if default == index:
			self._connection.settings["default"] = 0
		else:
			pass
			#TODO do something to update default if neededd

		self.loadSettings()

	def editParent(self):
		index = self.uiParentsTREE.currentIndex()
		definition = self._connection.settings["definitions"][index]
		cnxType = definition["type"]
		if cnxType == "slot":
			pass
		elif cnxType == "custom":
			pass
		elif cnxType == "mesh":
			pass
		elif cnxType == "nurbs":
			pass

	def move(self, direction="up"):
		index = self.uiKeySlotLIST.currentIndex()
		if index < 0:
			return

		newindex = index + 1 if direction == "down" else index - 1
		definitions = self._connection.settings["definitions"]
		if newindex < 0 or newindex > len(definitions) - 1:
			return

		definition = definitions.pop(index)
		definitions.insert(newindex, definition)

		default = self._connection.settings["default"]
		if default == index:
			self._connection.settings["default"] == newindex
		else:
			pass
			#TODO do something to update default if neededd

		self.saveSettings(definitions)
		self.loadSettings()
