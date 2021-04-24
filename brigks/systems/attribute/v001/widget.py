import copy

from Qt.QtGui import QRegExpValidator
from Qt.QtCore import QRegExp

from brigks.systems.systemWidget import SystemWidget


ATTR_TYPES = ["bool", "float", "short"]

class AttributeSystemWidget(SystemWidget):

	_blocked = False
	definitions = {}
	ordered = []
	
	def addWidgets(self):
		self.uiNameLINE.setValidator(QRegExpValidator(QRegExp('[A-Z][0-9a-zA-Z]+'), self.uiNameLINE))
		
	def addConnections(self):
		self.uiAddBTN.clicked.connect(self.addDefinition)
		self.uiDeleteBTN.clicked.connect(self.deleteDefinition)
		self.uiUpBTN.clicked.connect(lambda:self.moveDefinition("up"))
		self.uiDownBTN.clicked.connect(lambda:self.moveDefinition("down"))

		self.uiAttributeLIST.currentItemChanged.connect(self.loadDefinition)
		self.uiTypeCBOX.currentIndexChanged.connect(self.refresh)

		# Connect
		self.uiNameLINE.editingFinished.connect(self.nameChanged)
		self.uiTypeCBOX.currentIndexChanged.connect(self.definitionChanged)

		self.uiBooleanValueCHK.clicked.connect(self.definitionChanged)

		self.uiFloatValueSPN.valueChanged.connect(self.definitionChanged)
		self.uiFloatMinSPN.valueChanged.connect(self.definitionChanged)
		self.uiFloatMaxSPN.valueChanged.connect(self.definitionChanged)
		self.uiFloatHasMinCHK.clicked.connect(self.definitionChanged)
		self.uiFloatHasMaxCHK.clicked.connect(self.definitionChanged)
		self.uiFloatUIMinSPN.valueChanged.connect(self.definitionChanged)
		self.uiFloatUIMaxSPN.valueChanged.connect(self.definitionChanged)
		self.uiFloatHasUIMinCHK.clicked.connect(self.definitionChanged)
		self.uiFloatHasUIMaxCHK.clicked.connect(self.definitionChanged)

		self.uiIntegerValueSPN.valueChanged.connect(self.definitionChanged)
		self.uiIntegerMinSPN.valueChanged.connect(self.definitionChanged)
		self.uiIntegerMaxSPN.valueChanged.connect(self.definitionChanged)
		self.uiIntegerHasMinCHK.clicked.connect(self.definitionChanged)
		self.uiIntegerHasMaxCHK.clicked.connect(self.definitionChanged)
		self.uiIntegerUIMinSPN.valueChanged.connect(self.definitionChanged)
		self.uiIntegerUIMaxSPN.valueChanged.connect(self.definitionChanged)
		self.uiIntegerHasUIMinCHK.clicked.connect(self.definitionChanged)
		self.uiIntegerHasUIMaxCHK.clicked.connect(self.definitionChanged)
		
	def refresh(self):
		index = self.uiTypeCBOX.currentIndex()
		definitionWidgets = [self.uiBooleanDefinitionWDG,
							   self.uiFloatDefinitionWDG,
							   self.uiIntegerDefinitionWDG,
							   ]

		for i, wdg in enumerate(definitionWidgets):
			wdg.setVisible(i == index)


	# -------------------------------------------------------------
	# LOAD / SAVE
	# -------------------------------------------------------------
	def loadAttrs(self):
		self._definitions = copy.deepcopy(self.settings("definitions"))
		self._order = [attrName for attrName in self.settings("order") if attrName in self._definitions]

		for attrName in self._definitions.keys():
			if attrName not in self._order:
				self._order.append(attrName)

		self.uiAttributeLIST.clear()
		self.uiAttributeLIST.addItems(self._order)

		self.save()

	def loadDefinition(self):
		attrName = self.getCurrentAttrName()
		if not attrName:
			self.uiDefinitionGRP.setEnabled(False)
			return 

		self.uiDefinitionGRP.setEnabled(True)
		self._blocked = True

		definition = self._definitions[attrName]
		self.uiNameLINE.setText(attrName)

		type_ = definition["type"]
		self.uiTypeCBOX.setCurrentIndex(ATTR_TYPES.index(type_))

		if type_ == "Boolean":
			self.uiBooleanValueCHK.setChecked(definition["value"])
		elif type_ == "Float":
			self.uiFloatValueSPN.setValue(definition["value"])
			self.uiFloatHasMinCHK.setChecked(definition["hasMin"])
			self.uiFloatMinSPN.setValue(definition["min"])
			self.uiFloatHasMaxCHK.setChecked(definition["hasMax"])
			self.uiFloatMaxSPN.setValue(definition["max"])
			self.uiFloatHasUIMinCHK.setChecked(definition["hasUIMin"])
			self.uiFloatUIMinSPN.setValue(definition["uiMin"])
			self.uiFloatHasUIMaxCHK.setChecked(definition["hasUIMax"])
			self.uiFloatUIMaxSPN.setValue(definition["uiMax"])
		elif type_ == "Integer":
			self.uiIntegerValueSPN.setValue(definition["value"])
			self.uiIntegerHasMinCHK.setChecked(definition["hasMin"])
			self.uiIntegerMinSPN.setValue(definition["min"])
			self.uiIntegerHasMaxCHK.setChecked(definition["hasMax"])
			self.uiIntegerMaxSPN.setValue(definition["max"])
			self.uiIntegerHasUIMinCHK.setChecked(definition["hasUIMin"])
			self.uiIntegerUIMinSPN.setValue(definition["uiMin"])
			self.uiIntegerHasUIMaxCHK.setChecked(definition["hasUIMax"])
			self.uiIntegerUIMaxSPN.setValue(definition["uiMax"])

		self._blocked = False

	def save(self):
		if self._blocked:
			return 

		self.guide().setSettings(
			order=self._order, 
			definitions=copy.deepcopy(self._definitions)
			)


	# -------------------------------------------------------------
	# BUTTONS
	# -------------------------------------------------------------
	def addDefinition(self):
		attrName = self.getNextAvailableName("NewAttr")
		self.uiAttributeLIST.addItem(attrName)

		definition = dict(type="bool", value=False,
					hasMin=False, hasMax=False,
					min=0, max=1,
					hasUIMin=False, hasUIMax=False,
					uiMin=0, uiMax=1 )

		self._definitions[attrName] = definition
		self.orderChanged()

		self.uiAttributeLIST.setCurrentRow(self._order.index(attrName))

	def deleteDefinition(self):
		index = self.uiAttributeLIST.currentRow()
		item = self.uiAttributeLIST.takeItem(index)
		attrName = str(item.text())

		self._definitions.pop(attrName)
		self.orderChanged()

	def moveDefinition(self, direction="up"):
		index = self.uiAttributeLIST.currentRow()

		newIndex = index - 1 if direction == "up" else index + 1
		if newIndex < 0 or newIndex > self.uiAttributeLIST.count():
			return 

		item = self.uiAttributeLIST.takeItem(index)
		self.uiAttributeLIST.insertItem(newIndex, item)
		self.uiAttributeLIST.setCurrentItem(item)
		self.orderChanged()

	# -------------------------------------------------------------
	# EDIT
	# -------------------------------------------------------------
	def nameChanged(self):
		oldName = self.getCurrentAttrName()
		if not oldName:
			return 

		newName = str(self.uiNameLINE.text())
		if newName == oldName:
			return 

		newName = self.getNextAvailableName(newName)
 
		self._blocked = True
		self.uiNameLINE.setText(newName)
		item = self.uiAttributeLIST.currentItem()
		item.setText(newName)
		self._blocked = False

		self._order[self._order.index(oldName)] = newName
		self._definitions[newName] = self._definitions.pop(oldName)

		self.save()

	def definitionChanged(self):
		attrName = self.getCurrentAttrName()
		if not attrName:
			return 

		definition = self._definitions[attrName]

		type_ = str(self.uiTypeCBOX.currentText())
		definition["type"] = type_

		if type_ == "Boolean":
			definition["value"] = self.uiBooleanValueCHK.isChecked()
		elif type_ == "Float":
			definition["value"] = self.uiFloatValueSPN.value()
			definition["hasMin"] = self.uiFloatHasMinCHK.isChecked()
			definition["min"] = self.uiFloatMinSPN.value()
			definition["hasMax"] = self.uiFloatHasMaxCHK.isChecked()
			definition["max"] = self.uiFloatMaxSPN.value()
			definition["hasUIMin"] = self.uiFloatHasUIMinCHK.isChecked()
			definition["uiMin"] = self.uiFloatUIMinSPN.value()
			definition["hasUIMax"] = self.uiFloatHasUIMaxCHK.isChecked()
			definition["uiMax"] = self.uiFloatUIMaxSPN.value()
		elif type_ == "Integer":
			definition["value"] = self.uiIntegerValueSPN.value()
			definition["hasMin"] = self.uiIntegerHasMinCHK.isChecked()
			definition["min"] = self.uiIntegerMinSPN.value()
			definition["hasMax"] = self.uiIntegerHasMaxCHK.isChecked()
			definition["max"] = self.uiIntegerMaxSPN.value()
			definition["hasUIMin"] = self.uiIntegerHasUIMinCHK.isChecked()
			definition["uiMin"] = self.uiIntegerUIMinSPN.value()
			definition["hasUIMax"] = self.uiIntegerHasUIMaxCHK.isChecked()
			definition["uiMax"] = self.uiIntegerUIMaxSPN.value()

		self._definitions[attrName] = definition

		self.save()

	def orderChanged(self):
		self._order = []
		for index in xrange(self.uiAttributeLIST.count()):
			item = self.uiAttributeLIST.item(index)
			self._order.append(str(item.text()))

		self.save()

	# -------------------------------------------------------------
	# MISC
	# -------------------------------------------------------------
	def getCurrentAttrName(self):
		if not self.uiAttributeLIST.currentItem():
			return None, None

		attrName = str(self.uiAttributeLIST.currentItem().text())
		if attrName not in self._definitions:
			print "Harbie : ERROR : Params01 : Can't Find Attr in the list"
			return None, None

		return attrName

	def getNextAvailableName(self, name):
		if name not in self.settings("definitions"):
			return name

		i = 1
		while True:
			newName = name + str(i)
			if newName not in self.settings("definitions"):
				return newName

			i += 1 



			