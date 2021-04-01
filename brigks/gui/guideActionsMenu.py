
from Qt.QtWidgets import QMenu

#-------------------------------------------------------------------------------
# RIGHT CLICK MENU
#-------------------------------------------------------------------------------
class GuideActionsMenu(QMenu):
	
	def __init__(self, tree, parent=None):
		super(GuideActionsMenu, self).__init__(parent)
		
		self._tree = tree
		
		self.uiBuildACT = self.addAction("Build")