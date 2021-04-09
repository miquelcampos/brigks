from brigks.systems.systemBuilder import SystemBuilder


class DrivenSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createRig(None, "Driven")
		bfr = self.createBuffer(None, "Driven")
		ctl = self.createController(None, "Driven", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)