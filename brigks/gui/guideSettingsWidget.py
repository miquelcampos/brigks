import os.path

from Qt import QtCompat
from Qt.QtWidgets import QWidget

class GuideSettingsWidget(QWidget):

	def __init__(self, guide):
		super(GuideSettingsWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "guideSettingsWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._guide = guide
