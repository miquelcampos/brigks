import sip
import os.path

from Qt.QtWidgets import QWidget, QFileDialog

import maya.OpenMayaUI as mui
from maya import cmds

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QWidget)

def addScriptWidget(tempWindowName):
	if not cmds.window(tempWindowName, q=True, ex=True):
	    cmds.window(tempWindowName)
	    cmds.formLayout("qtLayoutObjects")

	ptr = mui.MQtUtil.mainWindow()
	mayaWindow = sip.wrapinstance(long(ptr), QWidget)
	for ind, el in enumerate(mayaWindow.children()):
	    try:
	        title = el.windowTitle()
	        if title == tempWindowName:
	            break
	    except:
	        continue

	cmds.setParent(tempWindowName+"|qtLayoutObjects")
	cmdsScriptEditor = cmds.cmdScrollFieldExecuter(sourceType="python", tabsForIndent=False, showTooltipHelp=False)#, modificationChangedCommand=self.codeModified)
	widget = el.children()[-1]
	widget.show()

	return widget


def fileDialog(parent, title, initPath, filters, save=True):
	filters = ";;".join(["%s (*.%s)"%(filter,filter) for filter in filters] + ["All files (*.*)"])
	fileDialog = QFileDialog(parent, title, initPath, filters)
	
	if save:
		fileDialog.setAcceptMode(QFileDialog.AcceptSave)
	else:
		fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
		
	fileDialog.exec_()
	if not fileDialog.result():
		return 
	
	path = str(fileDialog.selectedFiles()[0])
	if not save and not os.path.exists(path):
		return
		
	return path