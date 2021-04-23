
from Qt import QtCompat
from Qt.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QShortcut, QMessageBox
from Qt.QtGui import QKeySequence
from Qt.QtCore import Qt, QPoint

from brigks.gui.guideTreeWidgetItems import GuideTreeWidgetItem, LayerTreeWidgetItem, SystemTreeWidgetItem, SubSystemTreeWidgetItem
from brigks.gui.guideActionsMenu import GuideActionsMenu
from brigks.systems import getSystemGuideClass

class GuideTreeWidget(QTreeWidget):

	def __init__(self, guide=None):
		super(GuideTreeWidget, self).__init__()

		self.setColumnCount(2)
		self.setIndentation(10)
		self.setSelectionMode(self.ExtendedSelection)
		self.setDragDropMode(self.NoDragDrop)
		self.setHeaderHidden(True)

		header = self.header()
		header.setStretchLastSection(False)
		header.setMinimumSectionSize(60)
		QtCompat.QHeaderView.setSectionResizeMode(header, 0, QHeaderView.Stretch)
		QtCompat.QHeaderView.setSectionResizeMode(header, 1, QHeaderView.ResizeToContents)

		self.itemExpanded.connect(self.saveExpandedItem)
		self.itemCollapsed.connect(self.saveExpandedItem)

		self._guide = None
		self._menu = self.createRightClickMenu()

		if guide:
			self.setGuide(guide)

	def setGuide(self, guide):
		self.clear()
		self._guide = guide

		item = GuideTreeWidgetItem(self, guide)
		item.setExpanded(True)

	def selectedLayers(self):
		layers = []
		for item in self.selectedItems():
			if isinstance(item, LayerTreeWidgetItem):
				layers.append(item.layer())
		return layers

	def selectedSystems(self):
		systems = []
		for item in self.selectedItems():
			if isinstance(item, LayerTreeWidgetItem):
				systems.extend(item.systems())
			elif isinstance(item, (SystemTreeWidgetItem, SubSystemTreeWidgetItem)):
				systems.append(item.system())

		systems = list(set(systems))
		return systems

	def saveExpandedItem(self, item):
		if isinstance(item, LayerTreeWidgetItem):
			item.layer().settings()["expanded"] = item.isExpanded()

		self._guide.commit()

	#------------------------------------------------------
	# MENU
	#------------------------------------------------------
	def createRightClickMenu(self):
		menu = GuideActionsMenu(self)
		menu.uiAddGuideACT.triggered.connect(self.addGuide)
		menu.uiAddLayerACT.triggered.connect(self.addLayer)
		menu.uiAddSystemACT.triggered.connect(self.addSystem)
		menu.uiToggleGdeACT.triggered.connect(lambda:self.toggle(gde=True))
		menu.uiToggleRigACT.triggered.connect(lambda:self.toggle(rig=True))
		menu.uiToggleJntACT.triggered.connect(lambda:self.toggle(jnt=True))
		menu.uiToggleCtlACT.triggered.connect(lambda:self.toggle(ctl=True))
		menu.uiBuildACT.triggered.connect(self.build)
		menu.uiDuplicateACT.triggered.connect(self.duplicate)
		menu.uiMirrorACT.triggered.connect(self.mirror)
		menu.uiMirrorL2RACT.triggered.connect(self.mirrorL2R)
		# menu.uiMirrorR2LACT.triggered.connect(self.MirrorR2L)
		# menu.uiSnapACT.triggered.connect(self.snapSystem)
		menu.uiDeleteACT.triggered.connect(self.delete)
		menu.uiToSceneACT.triggered.connect(self.toScene)
		menu.uiFromSceneACT.triggered.connect(self.fromScene)

		QShortcut(QKeySequence(Qt.Key_H), self, lambda:self.toggle(gde=True))
		QShortcut(QKeySequence(Qt.Key_R), self, lambda:self.toggle(rig=True))
		QShortcut(QKeySequence(Qt.Key_J), self, lambda:self.toggle(jnt=True))
		QShortcut(QKeySequence(Qt.Key_C), self, lambda:self.toggle(ctl=True))
		QShortcut(QKeySequence(Qt.CTRL|Qt.Key_B), self, self.build)
		QShortcut(QKeySequence(Qt.CTRL|Qt.Key_D), self, self.duplicate)
		QShortcut(QKeySequence(Qt.CTRL|Qt.ALT|Qt.Key_D), self, self.mirror)
		QShortcut(QKeySequence.Delete, self, self.delete)
		QShortcut(QKeySequence(Qt.Key_F), self, self.toScene)
		QShortcut(QKeySequence(Qt.CTRL|Qt.Key_F), self, self.fromScene)

		return menu

	def mousePressEvent(self, event):
		super(GuideTreeWidget, self).mousePressEvent(event)

		# if not self._allowMenu:
		# 	event.accept()
		# 	return
		
		if event.button() == Qt.RightButton:
			if len(self.selectedItems()):
				# We add a little offset, otherwise we might click the first action accidentally
				pos = self.mapToGlobal(event.pos()+QPoint(-25,15))
				self._menu.filterActions()
				self._menu.exec_(pos)
				
		event.accept()

	#-------------------------------------------------------------------------------
	# ACTIONS
	#-------------------------------------------------------------------------------
	def addGuide(self):
		print "addGuide"

	def addLayer(self):
		parent = self._
		print "addLayer"

	def addSystem(self):
		layer = self.selectedLayers()[0]
		dialog = NewSystemDialog(self, self._guide, layer.name())
		if not dialog.exec_():
			return

		systemType = dialog.systemType()
		layer = dialog.layer()

		matrices = {}
		if dialog.pickPositions():
			SystemClass = getSystemGuideClass(systemType)
			matrices = SystemClass.pickMarkerPositions()
			if not matrices:
				return

		system = layer.addSystem(systemType, "M", "NewSystem", matrices, version=None)
		self._guide.commit()
		self.setGuide(self._guide)
			
	def toggle(self, gde=False, rig=False, jnt=False, ctl=False):
		systemGuides = self.selectedSystems()
		if not systemGuides:
			return 

		visible = not systemGuides[0].isVisible(gde, rig, jnt, ctl)
		for systemGuide in systemGuides:
			systemGuide.setVisible(visible, gde, rig, jnt, ctl)

	def build(self):
		self._guide.build(self.selectedSystems())
		self.setGuide(self._guide)

	def duplicate(self):
		for systemGuide in self.selectedSystems():
			systemGuide.duplicate(mirror=False)
		self._guide.commit()
		self.setGuide(self._guide)

	def mirror(self):
		for systemGuide in self.selectedSystems():
			systemGuide.mirror(duplicate=True)
		self._guide.commit()
		self.setGuide(self._guide)

	def mirrorL2R(self):
		print "mirrorL2R"
		print self.selectedSystems()

	def delete(self):
		msgBox = QMessageBox(QMessageBox.Question, "Delete", "Are you sure you want to delte those systems?", QMessageBox.Cancel, self)
		rigBTN = msgBox.addButton("Delete Rig", QMessageBox.ActionRole)
		GuideBTN = msgBox.addButton("Delete Rig and Guide", QMessageBox.ActionRole)
		rtn = msgBox.exec_()
		if rtn == QMessageBox.Cancel:
			return

		for systemGuide in self.selectedSystems():
			print "delete", systemGuide.key(), msgBox.clickedButton()==GuideBTN
			#systemGuide.delete(deleteGuide=(rtn==GuideBTN))
		self._guide.commit()
		self.setGuide(self._guide)

	def toScene(self):
		print "toScene"
		print self.selectedSystems()

	def fromScene(self):
		print "fromScene"

		

