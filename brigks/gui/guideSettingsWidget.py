import os.path
import sip

import maya.OpenMayaUI as mui
from maya import cmds

from Qt import QtCompat
from Qt.QtWidgets import QWidget

from brigks.gui.scriptWidget import ScriptWidget

class GuideSettingsWidget(QWidget):

	def __init__(self, guide):
		super(GuideSettingsWidget, self).__init__()
		uiPath = os.path.join(os.path.dirname(__file__), "ui", "guideSettingsWidget.ui")
		QtCompat.loadUi(uiPath, self)

		self._guide = guide

		self.uiPreScriptWDG = ScriptWidget("pre")
		self.uiScriptsTAB.layout().addWidget(self.uiPreScriptWDG)
		self.uiPostScriptWDG = ScriptWidget("post")
		self.uiScriptsTAB.layout().addWidget(self.uiPostScriptWDG)

		# Connect
		self.uiPreScriptWDG.updated.connect(self.scriptUpdated)
		self.uiPostScriptWDG.updated.connect(self.scriptUpdated)

	def setGuide(self, guide):
		self._guide = guide
		self.uiPreScriptWDG.setObject(self._guide)
		self.uiPostScriptWDG.setObject(self._guide)

	# ----------------------------------------------------------------------------------
	# SCRIPTS
	# ----------------------------------------------------------------------------------
	def scriptUpdated(self, settings):
		self._guide.setSettings(settings)
		self._guide.commit()