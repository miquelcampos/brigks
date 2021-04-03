import sip
from Qt.QtWidgets import QWidget
import maya.OpenMayaUI as mui

from marbieWindow import MarbieWindow


def showWindow():
	# Get Maya Window for parenting
	ptr = mui.MQtUtil.mainWindow()
	maya = sip.wrapinstance(long(ptr), QWidget)

	window = MarbieWindow(maya)

	window.show()