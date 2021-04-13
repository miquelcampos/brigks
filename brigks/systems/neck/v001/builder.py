from brigks.systems.systemBuilder import SystemBuilder


class NeckSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createRig(None, "X")
		bfr = self.createRig(None, "Hook1")
		bfr = self.createRig(None, "Hook2")
		bfr = self.createRig(None, "Hook3")