

from brigks.utils.gui import getMayaWindow
from brigks.gui.mainWindow import MainWindow

def showWindow():
	# Get Maya Window for parenting
	maya = getMayaWindow()
	window = MainWindow(maya)
	window.show()

