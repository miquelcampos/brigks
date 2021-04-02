from brigks.systems.systemBuilder import SystemBuilder


class FootSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createRig(None, "FkRef")
		bfr = self.createBuffer(None, "Fk")
		ctl = self.createController(None, "Fk", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)