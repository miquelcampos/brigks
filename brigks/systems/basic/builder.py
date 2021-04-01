from maya import cmds

from tools.marbie.systems.systemBuilder import SystemBuilder

class BasicSystemBuilder(SystemBuilder):


	def createObjects(self):
		
		for part, marker in self.guide.markers.iteritems():
			bfr = self.createBuffer(None, part, tfm=marker.transform())
			ctl = self.createController(bfr, part, tfm=marker.transform(), icon=None, size=1, po=None, ro=None, so=None, color=self.settings["colorIk"])
