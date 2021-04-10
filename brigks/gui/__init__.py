

from brigks.utils.gui import getMayaWindow
from brigks.gui.marbieWindow import MarbieWindow

def showWindow():
	# Get Maya Window for parenting
	maya = getMayaWindow()
	window = MarbieWindow(maya)
	window.show()

