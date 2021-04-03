import os.path

from Qt import QtCompat
from Qt.QtWidgets import QWidget, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QListWidget, QPlainTextEdit

class SystemWidget(QWidget):

	def __init__(self, system):
		super(SystemWidget, self).__init__()

		self._system = None
		self._widgets = None

		# Load UI File
		module = __import__(self.__module__, globals(), locals(), ["*"], -1)
		uiPath = os.path.join(os.path.dirname(module.__file__), "widget.ui")
		QtCompat.loadUi(uiPath, self)

		if system:
			self.setSystem(system)


	def setSystem(self, system):
		self._system = system

		if not self._widgets:
			self._widgets = self.getSettingWidgets()

		self.loadSettings()
		self.connectWidgets(self._widgets)

	# -----------------------------------------------------
	# WIDGETS
	# -----------------------------------------------------
	def getSettingWidgets(self):
		widgets = {}
		for setting in self._system.settings().keys():
			widgetName = "ui" + setting[0].capitalize() + setting[1:]
			if widgetName not in self.__dict__:
				continue
			widgets[setting] = self.__dict__[widgetName]
		return widgets
	
	def connectWidgets(self, widgets):
		for widget in widgets.values():
			widget.disconnect()
			if isinstance(widget, QCheckBox):
				widget.stateChanged.connect(self.saveSettings)
			elif isinstance(widget, QComboBox):
				widget.currentIndexChanged.connect(self.saveSettings)
			elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
				widget.valueChanged.connect(self.saveSettings)
			elif isinstance(widget, QLineEdit):
				widget.editingFinished.connect(self.saveSettings)
			elif isinstance(widget, QListWidget):
				widget.currentItemChanged.connect(self.saveSettings)
			elif isinstance(widget, QPlainTextEdit):
				widget.textChanged.connect(self.saveSettings)
	
	# -----------------------------------------------------
	# SETTINGS
	# -----------------------------------------------------
	def loadSettings(self):
		for setting, value in self._system.settings().items():
			if setting not in self._widgets:
				continue
			
			widget = self._widgets[setting]
			widget.blockSignals(True)
				
			if isinstance(widget, QCheckBox):
				widget.setChecked(value)
			elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
				widget.setValue(value)
			elif isinstance(widget, QLineEdit):
				widget.setText(value)
			elif isinstance(widget, QComboBox):
				allItems = [widget.itemText(i) for i in range(widget.count())]
				if value not in allItems:
					print "Invalid value for %s - %s"%(setting, value)
					continue
				widget.setCurrentIndex(allItems.index(value))
			elif isinstance(widget, QListWidget):
				for s in value:
					widget.addItem(s)
			elif isinstance(widget, QPlainTextEdit):
				widget.setPlainText(value)

			widget.blockSignals(False)
	
	def saveSettings(self):
		settings = {}
		for setting, widget in self._widgets.iteritems():
			if isinstance(widget, QCheckBox):
				settings[setting] = widget.isChecked()
			elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
				settings[setting] = widget.value()
			elif isinstance(widget, QLineEdit):
				settings[setting] = str(widget.text())
			elif isinstance(widget, QComboBox):
				settings[setting] = str(widget.currentText())
			elif isinstance(widget, QListWidget):
				settings[setting] = [str(widget.item(row).text()) for row in xrange(widget.count())]
			elif isinstance(widget, QPlainTextEdit):
				settings[setting] = str(widget.toPlainText())

		self._system.setSettings(settings)
		self._system.coreGuide.commit()