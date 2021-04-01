from tools.marbie.systems.systemBuilder import SystemBuilder


class LookatSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createRig(None, "Direction")
		bfr = self.createRig(None, "Local")
		bfr = self.createRig(None, "Offset")