import os.path
import sip

import maya.OpenMayaUI as mui
from maya import cmds

from Qt import QtCompat
from Qt.QtWidgets import QWidget, QInputDialog

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
		self.uiAddGroupBTN.clicked.connect(self.addGroup)
		self.uiRenameGroupBTN.clicked.connect(self.renameGroup)
		self.uiRemoveGroupBTN.clicked.connect(self.removeGroup)
		self.uiAddMembersBTN.clicked.connect(lambda:self.addRemoveMembers(add=True))
		self.uiRemoveMembersBTN.clicked.connect(lambda:self.addRemoveMembers(add=False))
		self.uiGroupsLIST.itemSelectionChanged.connect(self.loadMembers)
		self.uiMembersLIST.itemSelectionChanged.connect(self.selectScene)

		self.uiPreScriptWDG.updated.connect(self.scriptUpdated)
		self.uiPostScriptWDG.updated.connect(self.scriptUpdated)

		# Connection to Maya Select Event
		self._selectEventJobID = cmds.scriptJob(e=["SelectionChanged", self.selectMembers], protected=True)
	

	def closeEvent(self, event):
		cmds.scriptJob(kill=self._selectEventJobID, force=True)
		super(GuideSettingsWidget, self).closeEvent(event)

	def setGuide(self, guide):
		self._guide = guide
		self.loadGroups()
		self.uiPreScriptWDG.setObject(self._guide)
		self.uiPostScriptWDG.setObject(self._guide)

	# ----------------------------------------------------------------------------------
	# GROUPS
	# ----------------------------------------------------------------------------------\
	def loadGroups(self):
		self.uiGroupsLIST.clear()
		for groupName in self._guide.groups().keys():
			self.uiGroupsLIST.addItem(groupName)

		if self.uiGroupsLIST.count():
			self.uiGroupsLIST.setCurrentRow(0)

	def loadMembers(self):
		groupItem = self.uiGroupsLIST.currentItem()

		self.uiMembersLIST.clear()
		groupName = groupItem.text()
		members = [m.split("|")[-1] for m in self._guide.groups(groupName)]
		self.uiMembersLIST.addItems(members)
		self.uiMembersLIST.sortItems()

	def addGroup(self):
		groupName, rtn = QInputDialog.getText(self, "Group Name", "", text="GroupName")
		if not rtn or not groupName:
			return

		self.uiGroupsLIST.addItem(groupName)
		self._guide.addGroup(groupName)
		self._guide.commit()

	def renameGroup(self):
		groupItem = self.uiGroupsLIST.currentItem()
		groupName = groupItem.text()

		newName, rtn = QInputDialog.getText(self, "Group Name", "", text=groupName)
		if not rtn or not newName:
			return

		groupItem.setText(newName)
		self._guide.renameGroup(groupName, newName)
		self._guide.commit()

	def removeGroup(self):
		index = self.uiGroupsLIST.currentRow()
		groupItem = self.uiGroupsLIST.takeItem(index)
		self._guide.removeGroup(groupItem.text())
		self._guide.commit()

	def addRemoveMembers(self, add=True):
		groupItem = self.uiGroupsLIST.currentItem()
		groupName = groupItem.text()
		selection = cmds.ls(selection=True, type="transform", long=True)
		selection = [x for x in selection if x.startswith("|"+self._guide.setup())]

		if add:
			self._guide.addMembers(groupName, selection)
		else:
			self._guide.removeMembers(groupName, selection)

		self.loadMembers()
		self.selectMembers(selection)
		self._guide.commit()

	def selectMembers(self, selection=None):
		if selection is None:
			try:
				selection = cmds.ls(selection=True, type="transform", long=True)
			except AttributeError:
				pass

			selection = [x.split("|")[-1] for x in selection if x.startswith("|"+self._guide.setup())]
		selection = [x.split("|")[-1] for x in selection]
		for i in range(self.uiMembersLIST.count()):
			item = self.uiMembersLIST.item(i)
			item.setSelected(item.text() in selection)

	def selectScene(self):
		selection = []
		for item in self.uiMembersLIST.selectedItems():
			selection += cmds.ls(item.text(), type="transform", long=True)
		selection = [x for x in selection if x.startswith("|"+self._guide.setup())]
		cmds.select(selection)

	# ----------------------------------------------------------------------------------
	# SCRIPTS
	# ----------------------------------------------------------------------------------
	def scriptUpdated(self, settings):
		self._guide.setSettings(**settings)
		self._guide.commit()