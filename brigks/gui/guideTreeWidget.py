

from Qt.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from Qt import QtCompat

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

		if guide:
			self.setGuide(guide)

	def setGuide(self, guide):
		self.clear()
		self._guide = guide

		item = GuideTreeWidgetItem(self, guide)
		item.setExpanded(True)

	def selectedSystems(self):
		systems = []
		for item in self.selectedItems():
			if isinstance(item, LayerTreeWidgetItem):
				systems.extend(item.systems())
			else:
				systems.append(item.system)
		return systems

	def saveExpandedItem(self, item):
		if isinstance(item, LayerTreeWidgetItem):
			item.layer().settings()["expanded"] = True

		self._guide.dumps()

class GuideTreeWidgetItem(QTreeWidgetItem):

	def __init__(self, parent, guide):
		super(GuideTreeWidgetItem, self).__init__(parent, ["Guide"])

		self.guide = guide

		sortedLayers = sorted(guide.layers().items(), key=lambda x: x[0])
		for name, layer in sortedLayers:
			LayerTreeWidgetItem(self, name, layer)

class LayerTreeWidgetItem(QTreeWidgetItem):

	def __init__(self, parent, name, layer):
		super(LayerTreeWidgetItem, self).__init__(parent, [name])

		self._layer = layer
		self.setExpanded(self._layer.settings()["expanded"])

		sortedSubLayers = sorted(layer.layers().items(), key=lambda x: x[0])
		for subName, subLayer in sortedSubLayers:
			LayerTreeWidgetItem(self, subName, subLayer)

		sortedSystems = sorted(layer.systems().items(), key=lambda x: x[0])
		for key, system in sortedSystems:
			SystemTreeWidgetItem(self, key, system)

	def systems(self):
		systems = []
		for index in range(self.childCount()):
			item = self.child(index)
			if isinstance(item, LayerTreeWidgetItem):
				systems.extend(item.systems())
			else:
				systems.append(item.system)
		return systems

	def layer(self):
		return self._layer

class SystemTreeWidgetItem(QTreeWidgetItem):

	def __init__(self, parent, key, system):
		super(SystemTreeWidgetItem, self).__init__(parent, [key, system.type()])

		self._system = system

		if system.settings["location"] == "X":
			SubSystemTreeWidgetItem(self, key.replace("X", "L"), system)
			SubSystemTreeWidgetItem(self, key.replace("X", "R"), system)

	def system(self):
		return self._system


class SubSystemTreeWidgetItem(QTreeWidgetItem):

	def __init__(self, parent, key, system):
		super(SubSystemTreeWidgetItem, self).__init__(parent, [key])

		self._system = system

	def system(self):
		return self._system



