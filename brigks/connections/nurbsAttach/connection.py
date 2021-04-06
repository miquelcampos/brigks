from maya import cmds
from maya import OpenMaya as om

from brigks.connections.systemConnection import SystemConnection

class NurbsAttachSystemConnection(SystemConnection):

	def __init__(self):
		super(NurbsAttachSystemConnection, self).__init__()
		self._settings = dict(
			surface=None,
			u=.5,
			v=.5,
			useClosest=True,
			useOrientation=True,
			key=None,
			slot=None
			)

	def connect(self, child):
		if self._builder is None:
			raise RuntimeError("Cannot execture a connection without a Builder")

		position = cmds.xform(child, q=True, translation=True, worldSpace=True)
		parent = self.getParent(self._settings, position)
		self._parent(child, parent)

	def getTargetSystems(self):
		if self._settings["key"]:
			return [self._settings["key"]]
		return []
		
	def splitSymmetry(self, location):
		key = self._settings["key"]

		otherName, otherLocation = key.split("_")
		if otherLocation == "X":
			self._settings["key"] = "{n}_{l}".format(n=otherName, l=location)

	def getParent(self, settings, position):
		surface = settings["surface"]
		useClosest = settings["useClosest"]
		useOrientation = settings["useOrientation"]
		if useClosest:
			u, v = self._getClosestUV(surface, position, globalSpace=True)
		else:
			u = settings["u"]
			v = settings["v"]
		key = settings["key"]
		slot = settings["slot"]

		parent = None
		if key and slot:
			system = self._builder.coreBuilder.systems[key]
			parent = system.getObjectFromSlot(slot)
		if parent is None:
			parent = self._builder.coreBuilder.localCtl

		attachName = self.getObjectName(usage="Rig", part="MeshAttach")
		attach = cmds.createNode("transform", name=attachName)
		cmds.parent(attach, parent)
		cmds.xform(attach, translation=position, worldSpace=True)

		self._surfaceMultiAttach([[attach]], surface, 0, [u], [v])
		return attach


	def _getClosestUV(self, surface, point, globalSpace=True):
		'''Returns the Closest UV values on a NurbsSurface to 'point'

		Args:
			surface(MDagPath): dagPath to the nurbsSurface shapeNode
			point(MPoint): get the closest UV to this point
			globalSpace(bool): globalSpace?
		Returns:
			(list): float UV values
		'''
		if globalSpace:
			space = om.MSpace.kWorld
		else:
			space = om.MSpace.kObject

		point = om.MPoint(*point)

		#shape = cmds.listRelatives(surface, shapes=True, path=True)[0]
		fnSurface = self._getMFnNurbsSurface(surface)

		utilA = om.MScriptUtil()
		utilB = om.MScriptUtil()

		closestPointU = utilA.asDoublePtr()
		closestPointV = utilB.asDoublePtr()

		fnSurface.closestPoint(point, closestPointU, closestPointV, False, 1e-4, space)

		closestPointU = utilA.getDouble(closestPointU)
		closestPointV = utilB.getDouble(closestPointV)
		return [closestPointU, closestPointV]

	def _getMFnNurbsSurface(self, path):
		mobj = om.MObject()
		dagPath = om.MDagPath()
		selectionList = om.MSelectionList()
		selectionList.add(str(path))
		selectionList.getDependNode(0,mobj)


		selectionList.getDagPath(0, dagPath)

		return om.MFnNurbsSurface(dagPath)

	def _surfaceMultiAttach(self, slaves, surface, attach=0, uParams=None, vParams=None, evenly=False):
		'''
		Args:
			slaves(List of List of Transform): 
			surface(): 
			attach(int): 0 Parametric, 1 Percentage, 2 Fixed Length
			uParams(list of double|None): None for linear distribution. double must be between 0.0 and 1.0
			vParams(list of double|None): None for linear distribution. double must be between 0.0 and 1.0
		'''
		if not cmds.pluginInfo("HarbieNodes", q=True, loaded=True):
			cmds.loadPlugin("HarbieNodes")

		shape = cmds.listRelatives(surface, shapes=True, path=True)[0]

		vCount = len(slaves)
		uCount = len(slaves[0])

		if uParams is not None and len(uParams) != uCount:
			raise RuntimeError("Number of uParams doesn't match u count")
		if vParams is not None and len(vParams) != vCount:
			raise RuntimeError("Number of vParams doesn't match u count")

		
		# This is a custom command part of the Harbie Plugin
		length = cmds.surfaceInfo(surface, length=True)

		cmaNode = cmds.createNode("SurfaceMultiAttach", name="SrfMAttch")

		cmds.connectAttr(shape+".local", cmaNode+".surface")
		cmds.connectAttr(surface+".worldMatrix[0]", cmaNode+".surfaceMatrix")
		cmds.connectAttr(slaves[0][0]+".parentInverseMatrix[0]", cmaNode+".parentInverse")
		cmds.setAttr(cmaNode+".attach", attach)
		cmds.setAttr(cmaNode+".length", length)

		# V
		if vParams is None:
			if vCount == 1:
				vParams = [0.5]
			else:
				vParams = [j/float(vCount-1) for j in range(vCount)]
		
		# U
		if uParams is None:
			uParams = []
			if uCount == 1:
				uParams = [0.5]
			else:
				isClosed = cmds.getAttr(shape+".formU") != 0 
				count = float(uCount) if isClosed else float(uCount-1)
				for i in range(uCount):
					step = i/count
					if attach==0 and evenly:
						# This is a custom command part of the Harbie Plugin
						uParams.append(cmds.surfaceInfo(surface, pfp=step))
					else:
						uParams.append(step)

				
		for j, v in enumerate(vParams):
			cmds.setAttr(cmaNode+".v[%s]"%j, v)
		for i, u in enumerate(uParams):
			cmds.setAttr(cmaNode+".u[%s]"%i, u)


		for j in range(vCount):
			for i in range(uCount):
				index = j*uCount+i
				slave = slaves[j][i]
				cmds.connectAttr(cmaNode+".output[%s].translate"%index, slave+".translate")
				cmds.connectAttr(cmaNode+".output[%s].rotate"%index, slave+".rotate")

