

from brigks.systems.systemWidget import SystemWidget

# TODO

class TrackerSystemWidget(SystemWidget):
	definitions = {}
	ordered = []
	interpTypes = ["None","Linear","Smooth","Spline"]

	def addWidgets(self):
		self.uiGrabMinBTN.clicked.connect(lambda:self.grabFromRig("min"))
		self.uiGrabMaxBTN.clicked.connect(lambda:self.grabFromRig("max"))

		self.uiNameLINE.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[A-Z][0-9a-zA-Z]+'), self.uiNameLINE))

	def addConnections(self):
		self.uiAddBTN.clicked.connect(self.addParameterDefinition)
		self.uiRemoveBTN.clicked.connect(self.deleteParameterDefinition)
		self.uiUpBTN.clicked.connect(lambda : self.moveParameterDefinition("up"))
		self.uiDownBTN.clicked.connect(lambda : self.moveParameterDefinition("down"))

		self.uiDriverLIST.currentItemChanged.connect(self.loadDefinition)

		self.connectDefinitionChanged()

	def connectDefinitionChanged(self):
		self.uiNameLINE.editingFinished.connect(self.parameterNameChanged)
		self.uiInterpTypeCBOX.currentIndexChanged.connect(self.parameterDefinitionChanged)
		self.uiAxisCBOX.currentIndexChanged.connect(self.parameterDefinitionChanged)
		self.uiMinSPN.valueChanged.connect(self.parameterDefinitionChanged)
		self.uiMaxSPN.valueChanged.connect(self.parameterDefinitionChanged)

	def disconnectDefinitionChanged(self):
		self.uiNameLINE.editingFinished.disconnect(self.parameterNameChanged)
		self.uiInterpTypeCBOX.currentIndexChanged.disconnect(self.parameterDefinitionChanged)
		self.uiAxisCBOX.currentIndexChanged.disconnect(self.parameterDefinitionChanged)
		self.uiMinSPN.valueChanged.disconnect(self.parameterDefinitionChanged)
		self.uiMaxSPN.valueChanged.disconnect(self.parameterDefinitionChanged)

	# -------------------------------------------------------------
	# LOAD / SAVE
	# -------------------------------------------------------------
	def loadParameters(self):
		self._definitions = copy.deepcopy(self.parameters("driverDefs"))

		self.ordered = [paramName for paramName in self.parameters("driverDefOrder") if paramName in self._definitions]

		for paramName in self._definitions.keys():
			if paramName not in self.ordered:
				self.ordered.append(paramName)

		self.uiDriverLIST.clear()
		self.uiDriverLIST.addItems(self.ordered)

		self.saveParameters()

	def loadDefinition(self):
		paramName = self.getCurrentParameterName()
		if not paramName:
			self.uiDefinitionGRP.setEnabled(False)
			return 

		self.uiDefinitionGRP.setEnabled(True)

		self.disconnectDefinitionChanged()


		definition = self._definitions[paramName]
		self.uiNameLINE.setText(paramName)

		self.uiAxisCBOX.setCurrentIndex

		axis_ = definition["axis"]
		interpolation_ = definition["interpolation"]
		self.uiInterpTypeCBOX.setCurrentIndex(self.interpTypes.index(interpolation_))
		self.uiAxisCBOX.setCurrentIndex("XYZ".index(axis_))
		self.uiMinSPN.setValue(definition["min"])
		self.uiMaxSPN.setValue(definition["max"])

		self.connectDefinitionChanged()

	def saveParameters(self):
		parameters = {"driverDefOrder":self.ordered, "driverDefs":copy.deepcopy(self._definitions)}

		self.guide().setParameters(parameters)


	# -------------------------------------------------------------
	# BUTTONS
	# -------------------------------------------------------------
	def addParameterDefinition(self):
		paramName = self.getNextAvailableName("NewDriver")

		self.uiDriverLIST.addItem(paramName)


		definition = {	"axis":"Z",
					    "min":0,
					   	"max":0,
					   	"interpolation":"Linear"}

		self._definitions[paramName] = definition

		self.parameterOrderChanged()

		self.uiDriverLIST.setCurrentRow(self.ordered.index(paramName))

	def deleteParameterDefinition(self):
		index = self.uiDriverLIST.currentRow()
		item = self.uiDriverLIST.takeItem(index)
		paramName = str(item.text())

		self._definitions.pop(paramName)

		self.parameterOrderChanged()

	def moveParameterDefinition(self, direction="up"):
		index = self.uiDriverLIST.currentRow()

		newIndex = index - 1 if direction == "up" else index + 1
		if newIndex < 0 or newIndex > self.uiDriverLIST.count():
			return 

		item = self.uiDriverLIST.takeItem(index)
		self.uiDriverLIST.insertItem(newIndex, item)
		self.uiDriverLIST.setCurrentItem(item)

		self.parameterOrderChanged()

	def grabFromRig(self, minMax):
		if not self.access():
			self.warning("Tracker hasn't been built")
			return

		driverName = self.getCurrentParameterName()
		axis = "XYZ".index(self._definitions[driverName]["axis"])
		currentValue = self.access().attributes("setup", "OutRot").value()[axis]
		self._definitions[driverName][minMax] = currentValue

		self.saveParameters()
		self.loadDefinition()

		# set the value back into the rig, if created
		attr = self.access().attributes("setup", "%s%s"%(driverName, minMax.capitalize()))
		if attr:
			attr.setValue(currentValue)

	# -------------------------------------------------------------
	# EDIT
	# -------------------------------------------------------------
	def parameterNameChanged(self):
		oldName = self.getCurrentParameterName()
		if not oldName:
			return 

		newName = str(self.uiNameLINE.text())
		if newName == oldName:
			return 

		newName = self.getNextAvailableName(newName)

		self.disconnectDefinitionChanged()
		self.uiNameLINE.setText(newName)
		item = self.uiDriverLIST.currentItem()
		item.setText(newName)
		self.connectDefinitionChanged()

		self.ordered[self.ordered.index(oldName)] = newName
		self._definitions[newName] = self._definitions.pop(oldName)

		self.saveParameters()

	def parameterDefinitionChanged(self):
		paramName = self.getCurrentParameterName()
		if not paramName:
			return 

		definition = self._definitions[paramName]
		definition["interpolation"] = str(self.uiInterpTypeCBOX.currentText())
		definition["axis"] = str(self.uiAxisCBOX.currentText())
		definition["min"] = self.uiMinSPN.value()
		definition["max"] = self.uiMaxSPN.value()

		self._definitions[paramName] = definition

		self.saveParameters()

	def parameterOrderChanged(self):
		self.ordered = []
		for index in xrange(self.uiDriverLIST.count()):
			item = self.uiDriverLIST.item(index)
			self.ordered.append(str(item.text()))

		self.saveParameters()

	# -------------------------------------------------------------
	# MISC
	# -------------------------------------------------------------
	def getCurrentParameterName(self):
		if not self.uiDriverLIST.currentItem():
			return None, None

		paramName = str(self.uiDriverLIST.currentItem().text())
		if paramName not in self._definitions:
			print "Harbie : ERROR : Params01 : Can't Find Parameter in the list"
			return None, None

		return paramName

	def getNextAvailableName(self, name):
		if name not in self.parameters("driverDefs"):
			return name

		i = 1
		while True:
			newName = name + str(i)
			if newName not in self.parameters("driverDefs"):
				return newName

			i += 1 
