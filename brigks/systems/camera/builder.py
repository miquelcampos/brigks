from tools.marbie.systems.systemBuilder import SystemBuilder


class CameraSystemBuilder(SystemBuilder):

	def createObjects(self):

		bfr = self.createBuffer(None, "Camera", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)
		ctl = self.createController(None, "Camera", tfm=None, icon=None, size=1, po=None, ro=None, so=None, color=None)