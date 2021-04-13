from brigks.systems.systemBuilder import SystemBuilder


class DrivenSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createRig(None, "Driven")
		bfr = self.createBuffer(None, "Driven")
		ctl = self.createController(None, "Driven")