from maya import cmds
from brigks.connections.systemConnection import SystemConnection
from brigks import config

class FootLegAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(FootLegAttachSystemConnection, self).__init__()
		self._settings = dict(
			key=None
			)

	def connect(self):
		parentSystem = self.getSystem(self._settings["key"])
		if parentSystem is None:
			return

		parent_ikoffCtl = parentSystem.getObject(config.USE_CTL, "IkOffset")
		parent_footRef = parentSystem.getObject("FootRef")
		parent_blendAttr = parentSystem.attributes("Blend")
		if parentSystem.type() in ["leg"]:
			parent_footHook = parentSystem.getObject("Bone3")
		elif parentSystem.type() in ["zleg"]:
			parent_footHook = parentSystem.getObject("Bone4")

		# Not sure why Maya MPlug don't like being compared to None in a list
		if None in [root, lastbkCtl, fkRef] or blendAttr is None:
			return 

		root = self._builder.getObject("Root")
		lastbkCtl = self._builder.getObject(config.USE_CTL ,"Bk{}".format(self._builder.count("Part")))
		fkRef = self._builder.getObject("FkRef")
		blendAttr = self.attributes("Blend", "setup")
		
		self._parent(root, parent_ikoffCtl)
		self._parent(parent_ikRef, lastbkCtl)
		self._parent(fkRef, parent_footHook)
		cmds.connectAttr(parent_blendAttr, blendAttr)

	def getTargetSystems(self):
		if self._settings["key"]:
			return [self._settings["key"]]
		return []

	def split(self, location):
		key = self._settings["key"]

		otherName, otherLocation = key.split("_")
		if otherLocation == "X":
			self._settings["key"] = "{n}_{l}".format(n=otherName, l=location)
