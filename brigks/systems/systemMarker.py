from maya import cmds

from math3d import Transformation, Matrix4, Vector3

from brigks.core import naming
from brigks.utils import create

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

class SystemMarker(object):

	def __init__(self, marker, system):
		self._marker = marker
		self._system = system
		self._matrix = None
		self._transformWithScale = None
		self._transform = None
		self._translation = None
		self._scale = None

	def name(self):
		return self._marker

	@classmethod
	def create(cls, name, system, parent, matrix=None):
		parent = parent._marker if isinstance(parent, cls) else parent
		node = create.transform(parent, name, matrix, color=[1,1,0])
		create.icon("sphere", node, size=.5)
		#cmds.xform(node, matrix=matrix, worldSpace=True)
		return cls(node, system)

	def rename(self, newName):
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
			self._transform = Matrix4(self._matrix).asTransform()
			self._translation = self._transform.translation
			self._scale = self._transform.scale
			self._transform.scale = Vector3([1,1,1])

		return self._transform

	def translation(self):
		if self._translation is None:
			translation = cmds.xform(self._marker, q=True, translation=True, worldSpace=True)
			self._translation = Vector3(translation)

		return self._translation

	def direction(self, axis="x"):
		tfm = self.transform()
		return tfm.rotation.asMatrix()["xyz".index(axis)]