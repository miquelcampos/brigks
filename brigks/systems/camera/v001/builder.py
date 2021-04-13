from brigks.systems.systemBuilder import SystemBuilder


class CameraSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createBuffer(None, "Camera")
		ctl = self.createController(None, "Camera")