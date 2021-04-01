import os.path
from Qt import QtCompat

from tools.marbie.connections.systemConnectionWidget import SystemConnectionWidget
from tools.marbie.gui.pickSlotDialog import PickSlotDialog


class SlotParentConnectionWidget(SystemConnectionWidget):

	def __init__(self, connection, system):
		super(SlotParentConnectionWidget, self).__init__(connection, system)
		uiPath = os.path.join(os.path.dirname(__file__), "widget.ui")
		QtCompat.loadUi(uiPath, self)

		self.uiPickBTN.clicked.connect(self.pickSlot)

	def pickSlot(self):
		dialog = PickSlotDialog(self, self._system.coreGuide)
		if not dialog.exec_():
			return

		self.uiKey.setText(dialog.systemKey())
		self.uiSlot.setText(dialog.systemSlot())
		self.saveSettings()