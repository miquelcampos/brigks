import os.path
import sip
from maya import cmds

from Qt.QtWidgets import QDialog
from Qt import QtCompat

from brigks import Guide
from brigks.gui.guideTreeWidget import GuideTreeWidget, GuideTreeWidgetItem, LayerTreeWidgetItem, SystemTreeWidgetItem, SubSystemTreeWidgetItem
from brigks.gui.guideSettingsWidget import GuideSettingsWidget
from brigks.gui.layerSettingsWidget import LayerSettingsWidget
from brigks.gui.systemSettingsWidget import SystemSettingsWidget

class MarbieWindow(QDialog):

	def __init__(self, parent=None):
		super(MarbieWindow, self).__init__(parent)
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "marbieWindow.ui")
		QtCompat.loadUi(uiPath, self)

		self._guide = None
		self._settingsWidget = None
		self._guideSettingsWidget = GuideSettingsWidget(self._guide)
		self._layerSettingsWidget = None
		self._systemSettingsWidget = None

		self.uiGuideTREE = GuideTreeWidget()
		self.uiTreeWDG.layout().addWidget(self.uiGuideTREE)

		self.loadGuide()

		self.uiGuideTREE.itemSelectionChanged.connect(self.loadSettings)

		self.loadSettings()

	def loadGuide(self):
		# Find Guides
		for guideAttr in cmds.ls("*.guide"):
			guide, attr = guideAttr.split(".")
			self._guide = Guide(model=guide)
			self.uiGuideTREE.setGuide(self._guide)
			break

	def loadSettings(self):
		# Clear
		if self._settingsWidget:
			self.uiSettingsWDG.layout().removeWidget(self._settingsWidget)
			self._settingsWidget.setVisible(False)

		items = self.uiGuideTREE.selectedItems()
		if not items or isinstance(items[0], GuideTreeWidgetItem):
			self._settingsWidget = self._guideSettingsWidget
		elif isinstance(items[0], LayerTreeWidgetItem):
			if not self._layerSettingsWidget:
				self._layerSettingsWidget = LayerSettingsWidget(items[0].layer())
			else:
				self._layerSettingsWidget.setLayer(items[0].layer())
			self._settingsWidget = self._layerSettingsWidget
		elif isinstance(items[0], (SystemTreeWidgetItem, SubSystemTreeWidgetItem)):
			if not self._systemSettingsWidget:
				self._systemSettingsWidget = SystemSettingsWidget(items[0].system())
			else:
				self._systemSettingsWidget.setSystem(items[0].system())
			self._settingsWidget = self._systemSettingsWidget

		self.uiSettingsWDG.layout().addWidget(self._settingsWidget)
		self._settingsWidget.setVisible(True)
