import os.path

from Qt.QtWidgets import QDialog
from Qt import QtCompat

from brigks.systems import getSystemList

class NewSystemDialog(QDialog):

	def __init__(self, parent, guide, defaultLayer=None):
		super(NewSystemDialog, self).__init__(parent)
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "newSystemDialog.ui")
		QtCompat.loadUi(uiPath, self)

		self._guide = guide
		self._defaultLayer = defaultLayer
		self._systemsByCategory = {}
		self.setLayer(layer)

		self.uiCategoryCBOX.currentIndexChanged.connect(setSystemList)

	def setLayer(self, layer):
		layers = sorted(self._guide.layers().keys())
		default = layers.index(self._defaultLayer) if self._defaultLayer else 0
		
		self.uiLayerCBOX.clear()
		self.uiLayerCBOX.addItems(layers)
		self.uiLayerCBOX.setCurrentIndex(default)

		self._systemsByCategory = getSystemListByCategory()
		categories = sorted(self._systemsByCategory.keys())
		self.uiCategoryCBOX.clear()
		self.uiCategoryCBOX.addItems(categories)
		self.uiCategoryCBOX.setCurrentIndex(categories.index("ALL"))

		self.setSystemList()

	def setSystemList(self):
		category = self.uiCategoryCBOX.currentText()
		systems = sorted(self._systemsByCategory[category])

		self.uiSystemTypeLIST.clear()
		self.uiSystemTypeLIST.addItems(systems)
		self.uiSystemTypeLIST.setCurrentIndex(0)

	# ----------------------------------------------------------------------------------
	# RETURN
	# ----------------------------------------------------------------------------------
	def layer(self):
		layer = self._guide.layers(self.uiLayerCBOX.currentText())

	def systemType(self):
		return self.uiSystemTypeLIST.currentItem().text()

	def pickPositions(self):
		return self.uiPickPositionCHK.isChecked()
