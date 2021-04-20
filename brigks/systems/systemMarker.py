from copy import copy

from maya import cmds

from math3d import Transformation, Matrix4, Vector3

from brigks import naming
from brigks.utils import create

class SystemMarker(object):

	def __init__(self, marker, system):
		self._marker = marker
		self._system = system

		self._mirrored = False

		self._matrix = None
		self._transformWithScale = None
		self._transform = None
		self._translation = None
		self._scale = None

	def name(self):
		return self._marker

	def setMirrored(self, mirrored):
		self._mirrored = mirrored
		# Makes sure that the transform wasn't stored
		self._matrix = None
		self._transformWithScale = None
		self._transform = None
		self._translation = None
		self._scale = None

	@classmethod
	def create(cls, name, system, parent, matrix=None):
		parent = parent._marker if isinstance(parent, cls) else parent
		node = create.transform(name, parent, matrix, color=[1,1,0])
		create.icon("sphere", node, size=.5)
		#cmds.xform(node, matrix=matrix, worldSpace=True)
		return cls(node, system)

	def rename(self, newName):
		modelName = self._marker.split("|")[1]
		shortName = self._marker.split("|")[-1]
		self._marker = [m for m in cmds.ls(shortName, long=True) if m.startswith("|"+modelName)][0]
		self._marker = cmds.rename(self._marker, newName)

	def setTransform(self, transform):
		matrix = transform.asMatrix().flattened()
		cmds.xform(self._marker, matrix=matrix, worldSpace=True)

	def matrix(self):
		if self._matrix is None:
			self.transform()
		return self._matrix

	def transformWithScale(self):
		if self._transformWithScale is None:
			self.transform()
		return self._transformWithScale

	def transform(self):
		if self._transform is None:
			self._matrix = cmds.xform(self._marker, q=True, matrix=True, worldSpace=True)
			self._transformWithScale = Matrix4(self._matrix).asTransform()
			if self._mirrored:
				self._transformWithScale = self._transformWithScale.mirrored()

			self._transform = copy(self._transformWithScale)
			self._transform.scale = Vector3([1,1,1])
			self._translation = self._transform.translation
			self._scale = self._transform.scale

		return self._transform

	def translation(self):
		if self._translation is None:
			translation = cmds.xform(self._marker, q=True, translation=True, worldSpace=True)
			self._translation = Vector3(translation)
			if self._mirrored:
				self._translation.x = -self._translation.x

		return self._translation

	def scale(self):
		if self._scale is None:
			self.transform()

		return self._scale

	def direction(self, axis="x"):
		tfm = self.transform()
		return tfm.rotation.asMatrix()["xyz".index(axis)]

# ----------------------------------------------------------------------------------
# ITERATE MARKERS
# ----------------------------------------------------------------------------------
def checkMarkersMinMax(markers, markerNames, markerMinMax):
	"""Checks that all the mandatory markers exist.
	It return the name of the marker and the object from the dictionary if it is found

	Args:
	    markers (dict): Dictionary 
	    markerNames (set): Set of marker names
	    markerMinMax (set): Set of marker MinMax

	Returns:
	    bool: Description of return value
	"""
	for name in markerNames:
		if name in markerMinMax:
			markerMin, markerMax = markerMinMax[name]
			limit = lambda x: x <= markerMax if markerMax > 0 else lambda i: True

			i = 1
			while limit(i):
				part = "{}{}".format(name, i)
				if part not in markers:
					break
				yield part, markers[part]
				i += 1

			# Not enough
			for i in range(i, markerMin+1):
				part = "{}{}".format(name, i)
				yield part, None

		else:
			if name in markers:
				yield name, markers[name]
			else:
				yield name, None