from brigks.systems.systemBuilder import SystemBuilder


class PistonSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createBuffer(None, "Breast", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		ctl = self.createController(None, "Breast", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)