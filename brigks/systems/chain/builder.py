from brigks.systems.systemBuilder import SystemBuilder


class ChainSystemBuilder(SystemBuilder):

	def createObjects(self):

		for i, (part, marker) in enumerate(self.guide.markers.iteritems()):
			fkName = "Fk{}".format(i)
			boneName = "Bone{}".format(i)
			dynName = "Dynamic{}".format(i)

			bfr = self.createBuffer(None, fkName, tfm=marker.transform())
			ctl = self.createController(bfr, fkName, tfm=marker.transform(), icon=None, size=1, po=None, ro=None, so=None, color=self.settings["colorIk"])

			bone = self.createRig(None, boneName, tfm=marker.transform())
			dyn = self.createRig(None, dynName, tfm=marker.transform())
