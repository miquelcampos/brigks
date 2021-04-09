from brigks.systems.systemBuilder import SystemBuilder


class AverageSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createBuffer(None, "Average", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		ctl = self.createController(None, "Average", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)