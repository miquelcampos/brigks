import os.path
import sip

from Qt import QtCompat
from Qt.QtWidgets import QWidget

from brigks.systems import getSystemList, getSystemWidgetClass
from brigks.gui.connectionWidget import ConnectionWidget

SYSTEM_TYPES = getSystemList()
SYSTEM_LOCATIONS = ["M", "L", "R", "X"]

class SystemSettingsWidget(QWidget):

	def __init__(self, system):
		super(SystemSettingsWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "systemSettingsWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._system = None
		self._connectionWidgets = {}
		self._settingsWidgets = {}
		self._settingsWidget = None

		# Common
		# self.uiTypeCBOX.currentIndexChanged.connect(self.save)
		# self.uiLocationCBOX.currentIndexChanged.connect(self.save)
		# self.uiNameLINE.editingFinished.connect(self.save)

		if system:
			self.setSystem(system)

		# Connect Signals
		self.uiAddConnectionBTN.clicked.connect(self.addConnection)
		self.uiConnectionPortCBOX.currentIndexChanged.connect(self.loadConnectionTypes)

	def setSystem(self, system):
		self._system = system

		# Common
		systemTypeTitles = [t.title() for t in SYSTEM_TYPES]

		self.uiTypeCBOX.clear()
		self.uiTypeCBOX.addItems(systemTypeTitles)
		self.uiTypeCBOX.setCurrentIndex(SYSTEM_TYPES.index(system.type()))

		self.uiLocationCBOX.setCurrentIndex(SYSTEM_LOCATIONS.index(system.settings()["location"]))

		self.uiNameLINE.setText(system.settings()["name"])

		# Add Connections Widget
		self.clearConnectionWidgets()
		connections = sorted(system.connections().items(), key=lambda x: x[0])
		for port, connection in connections:
			self.addConnectionWidget(port, connection)

		# Settings
		if self._settingsWidget:
			self.uiSettingsTAB.layout().removeWidget(self._settingsWidget)
			self._settingsWidget.setVisible(False)

		if system.type() not in self._settingsWidgets:
			WidgetClass = getSystemWidgetClass(system.type())
			self._settingsWidgets[system.type()] = WidgetClass(system)
		else:
			self._settingsWidgets[system.type()].setSystem(system)

		self._settingsWidget = self._settingsWidgets[system.type()]
		self.uiSettingsTAB.layout().addWidget(self._settingsWidget)
		self._settingsWidget.setVisible(True)

	def save(self):
		if not self._system:
			return

		self._system.settings()["location"] = SYSTEM_LOCATIONS[self.uiLocationCBOX.currentIndex()]
		self._system.settings()["name"] = self.uiNameLINE.currentText()

		self._system.coreGuide.dumps()

	# ----------------------------------------------------------------------------------
	# CONNECTIONS
	# ----------------------------------------------------------------------------------
	def clearConnectionWidgets(self):
		for widget in self._connectionWidgets.values():
			self.uiConnectionsLAY.removeWidget(widget)
			sip.delete(widget)
		self._connectionWidgets = {}

	def updateConnectionWidgets(self):
		hasPortAvailable = len(self.portsAvailable()) > 0
		self.uiAddConnectionBTN.setEnabled(hasPortAvailable)
		self.uiConnectionPortCBOX.setEnabled(hasPortAvailable)
		self.uiConnectionTypeCBOX.setEnabled(hasPortAvailable)

		self.loadConnectionPorts()
		self.loadConnectionTypes()

	def portsAvailable(self):
		allPorts = self._system.connectionPorts().keys()
		cnxPorts = self._system.connections().keys()
		return [p for p in allPorts if p not in cnxPorts]

	def loadConnectionPorts(self):
		self.uiConnectionPortCBOX.clear()
		self.uiConnectionPortCBOX.addItems(sorted(self.portsAvailable()))

	def loadConnectionTypes(self):
		self.uiConnectionTypeCBOX.clear()
		port = self.uiConnectionPortCBOX.currentText()
		if port:
			types = self._system.connectionPorts()[port]
			self.uiConnectionTypeCBOX.addItems(types)

	def addConnection(self):
		port = self.uiConnectionPortCBOX.currentText()
		connectionType = self.uiConnectionTypeCBOX.currentText()

		connection = self._system.addConnection(connectionType, port)
		self.addConnectionWidget(port, connection)

		self._system.coreGuide.dumps()

	def addConnectionWidget(self, port, connection):
		if port in self._connectionWidgets:
			raise RuntimeError("Port {} already exists".format(port))

		widget = ConnectionWidget(port, connection, self._system)
		widget.deleted.connect(lambda: self.deleteConnectionWidget(port))
		self.uiConnectionsLAY.addWidget(widget)
		self._connectionWidgets[port] = widget

		self.updateConnectionWidgets()

	def deleteConnectionWidget(self, port):
		# Delete Connection from System
		self._system.deleteConnection(port)
		self._system.coreGuide.dumps()

		# Delete Connection Widget
		widget = self._connectionWidgets.pop(port)
		self.uiConnectionsLAY.removeWidget(widget)
		sip.delete(widget)

		self.updateConnectionWidgets()
