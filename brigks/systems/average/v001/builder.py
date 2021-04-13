from brigks.systems.systemBuilder import SystemBuilder


class AverageSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createBuffer(None, "Average", tfm=None)
		ctl = self.createController(bfr, "Average", tfm=None)