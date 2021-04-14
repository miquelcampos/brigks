from itertools import izip

from maya import cmds

from math3d.transformation import Transformation

from brigks.utils import attributes, compounds
from brigks.systems.systemBuilder import SystemBuilder

class SliderSystemBuilder(SystemBuilder):

	def createObjects(self):
		# TRANSFORMATION
		rootTfm = self.transforms("Rail")
		posTfm = [Transformation.fromParts(translation=pos, rotation=tfm.rotation) for tfm, pos in izip(rootTfm, self.translations("Pos"))]
		negTfm = [Transformation.fromParts(translation=pos, rotation=tfm.rotation) for tfm, pos in izip(rootTfm, self.translations("Neg"))]
		
		# CONTROLLERS
		self._lmts = []
		self._rails = []
		self._psts = []
		self._ngts = []
		self._slds = []
		self._ctls = []
		
		for i, (rtfm, ptfm, ntfm) in enumerate(izip(rootTfm, posTfm, negTfm), start=1):
			irtfm = rtfm.asMatrix().inverse()
			irtfm = irtfm.asTransform()

			p = ptfm * irtfm
			limit_max = p.translation.x

			p = ntfm * irtfm
			limit_min = p.translation.x

			
			length = limit_max - limit_min
			offset = length*.5 + limit_min
			
			self._lmts.append([limit_min, limit_max])

			rail = self.createRig(None, "Rail{}".format(i), rtfm, "cube", size=1, 
				po=(offset,0,0), so=(abs(length), .5, .5))
						
			slider = self.createRig(rail, "Slider{}".format(i), rtfm, "cube")	

			if self.settings("addControllers"):
				ctl = self.createController(slider, "Slider{}".format(i), rtfm, "cube", color=self.colorIk())
				self._ctls.append(ctl)

			attributes.setKeyables(slider)
			
			self._psts.append(None)
			self._ngts.append(None)

			self._rails.append(rail)
			self._slds.append(slider)

	def createDeformers(self):
		parents = self._ctls if self.settings("addControllers") else self._slds
		for i, slider in enumerate(parents, start=1):
			self.createJoint(slider, str(i))

	#----------------------------------------------------------------------------
	# PROPERTIES
	def createAttributes(self):
		self.outrotAttr = self.createSetupAttr("OutRot", "float3", (0,0,0))

	#----------------------------------------------------------------------------
	# OPERATORS
	def createOperators(self):
		rots = [(self.settings("minRot{}".format(i)), self.settings("maxRot{}".format(i))) for i in xrange(1, self.count("Rail")+1)]
		axis = ["XYZ".index(self.settings("axis{}".format(i))) for i in xrange(1, self.count("Rail")+1)]
		for rail, pos, neg, slider, limits, rot, a in izip(self._rails, self._psts, self._ngts, self._slds, self._lmts, rots, axis):
			
			cns = compounds.rotationToSlider(slider+".tx", rotMin=rot[0], rotMax=rot[1], 
										slideMin=limits[0], slideMax=limits[1])

			cmds.connectAttr(self.outrotAttr+str(a), cns+".angle")

	#----------------------------------------------------------------------------
	# CONNECTION
	def createConnections(self):
		for port, cnx in self.connections().iteritems():
			if port == "Tracker":
				cnx.connect(self.outrotAttr)
			else:
				child = self.getObject("Rig", port)
				cnx.connect(child)