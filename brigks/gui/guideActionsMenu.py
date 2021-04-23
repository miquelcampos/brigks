
from Qt.QtWidgets import QMenu
from Qt.QtGui import QKeySequence
from Qt.QtCore import Qt

from brigks.gui.guideTreeWidgetItems import GuideTreeWidgetItem, LayerTreeWidgetItem, SystemTreeWidgetItem, SubSystemTreeWidgetItem

#-------------------------------------------------------------------------------
# RIGHT CLICK MENU
#-------------------------------------------------------------------------------
class GuideActionsMenu(QMenu):
	
	def __init__(self, tree, parent=None):
		super(GuideActionsMenu, self).__init__(parent)

		self._tree = tree
		
		# Actions
		self.uiAddGuideACT = self.addAction("Add Guide")
		self.uiAddLayerACT = self.addAction("Add Layer")
		self.uiAddSystemACT = self.addAction("Add System")
		self.addSeparator()
		self.uiToggleGdeACT = self.addAction("Toggle Vis Gde")
		self.uiToggleGdeACT.setShortcut(QKeySequence(Qt.Key_H))
		self.uiToggleRigACT = self.addAction("Toggle Vis Rig")
		self.uiToggleRigACT.setShortcut(QKeySequence(Qt.Key_R))
		self.uiToggleJntACT = self.addAction("Toggle Vis Jnt")
		self.uiToggleJntACT.setShortcut(QKeySequence(Qt.Key_J))
		self.uiToggleCtlACT = self.addAction("Toggle Vis Ctl")
		self.uiToggleCtlACT.setShortcut(QKeySequence(Qt.Key_C))
		self.addSeparator()
		self.uiBuildACT = self.addAction("Build")
		self.uiBuildACT.setShortcut(QKeySequence(Qt.CTRL|Qt.Key_B))
		self.uiDuplicateACT = self.addAction("Duplicate")
		self.uiDuplicateACT.setShortcut(QKeySequence(Qt.CTRL|Qt.Key_D))
		self.uiMirrorACT = self.addAction("Mirror")
		self.uiMirrorACT.setShortcut(QKeySequence(Qt.CTRL|Qt.ALT|Qt.Key_D))
		self.uiMirrorL2RACT = self.addAction("Mirror L to R")
		# self.uiMirrorR2LACT = self.addAction("Mirror R to L")
		# self.uiSnapACT = self.addAction("Snap")
		self.addSeparator()
		self.uiDeleteACT = self.addAction("Delete")
		self.uiDeleteACT.setShortcut(QKeySequence.Delete)
		self.addSeparator()
		self.uiToSceneACT = self.addAction("Select in Scene")
		self.uiToSceneACT.setShortcut(QKeySequence(Qt.Key_F))
		self.uiFromSceneACT = self.addAction("Select from Scene")
		self.uiFromSceneACT.setShortcut(QKeySequence(Qt.CTRL|Qt.Key_F))
	
	def filterActions(self):
		guideSelected = []
		layerSelected = []
		systemSelected = []
		
		for item in self._tree.selectedItems():
			if isinstance(item, GuideTreeWidgetItem):
				guideSelected.append(item.guide())
			elif isinstance(item, LayerTreeWidgetItem):
				layerSelected.append(item.layer())
			elif isinstance(item, (SystemTreeWidgetItem, SubSystemTreeWidgetItem)):
				systemSelected.append(item.system())
				
		# Actions Visible
		isLayerOnly = len(layerSelected) == 1 and not len(guideSelected) == 0 and not len(systemSelected) == 0
		isOneLayer = isLayerOnly and (len(layerSelected) == 1)
		isSystemOnly = len(systemSelected) == 1 and not len(guideSelected) == 0 and not len(layerSelected) == 0
		isSystemOrLayer = not guideSelected
		isGuideOrLayer = not systemSelected
		isOneGuideOrOneLayer = isGuideOrLayer and (len(layerSelected+guideSelected) == 1)
		
		self.uiAddGuideACT.setVisible(isOneGuideOrOneLayer)
		self.uiAddLayerACT.setVisible(isOneGuideOrOneLayer)
		self.uiAddSystemACT.setVisible(isOneLayer)

		self.uiDuplicateACT.setVisible(isSystemOnly) 
		self.uiMirrorACT.setVisible(isSystemOnly) 
		self.uiMirrorL2RACT.setVisible(isLayerOnly)
		# self.uiMirrorR2LACT.setVisible(isLayerOnly)

		self.uiToSceneACT.setVisible(isSystemOrLayer) 
