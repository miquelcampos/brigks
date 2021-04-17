from brigks.systems.systemBuilder import SystemBuilder


class PistonSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createBuffer(None, "Breast", tfm=None)
		ctl = self.createController(None, "Breast", tfm=None)