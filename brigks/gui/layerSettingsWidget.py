import os.path

from Qt import QtCompat
from Qt.QtWidgets import QWidget

class LayerSettingsWidget(QWidget):

	def __init__(self, layer):
		super(LayerSettingsWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "layerSettingsWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self.setLayer(layer)

	def setLayer(self, layer):
		self._layer = layer
