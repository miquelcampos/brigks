from maya import cmds

from math3d.transformation import Transformation

from brigks.systems.systemBuilder import SystemBuilder
from brigks.utils import create
from brigks import config

class CameraSystemBuilder(SystemBuilder):


	def createObjects(self):
		# TRANSFORMATION
		tfm = Transformation.lookAt(self.translations("Root"), self.directions("Root", "y"), self.directions("Root", "z"), "y"+self.sign()+"z", False)
		
		# OBJECTS
		bfr = self.addBfr(None, "Camera", tfm) 
		camera = self.addCamera(bfr, "Camera", tfm=tfm)
		# shape = cmds.listRelatives(camera, shapes=True)[0]

		# # Match Settings from guide
		# marker = cmds.listRelatives(self.markers("Root").name(), shapes=True)

		# for name in ["focalLength", "cameraScale", "nearClipPlane", "farClipPlane", 
		# 		"horizontalFilmAperture", "verticalFilmAperture", "lensSqueezeRatio", 
		# 		"filmFit", "filmFitOffset", "horizontalFilmOffset", "verticalFilmOffset"]:

		# 	value = cmds.getAttr(marker+"."+name)
		# 	cmds.setAttr(shape+"."+name, value)


	def createConnections(self):
		if "Root" in self.connections():
			root = self.getObject(config.USE_BFR, "Camera")
			self.connections("Root").connect(root)
