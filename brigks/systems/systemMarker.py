from maya import cmds

# TODO: Replace with new math3D linbray
# from cross3d.xmathutils import Transform, Matrix, Vector
from math3d import Transformation, Matrix4, Vector3

def checkMarkersMinMax(markers, markerNames, markerMinMax):
	"""
	Checks that all the mandatory markers exist.
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

	def __init__(self, marker):
		self._marker = marker
		self._transform = None
		self._translation = None

	@classmethod
	def create(cls, name, parent, matrix=None):
		node = cmds.spaceLocator(name=name)
		if matrix is not None:
			cmds.xform(node, matrix=matrix, worldSpace=True)
		parent = parent._marker if isinstance(parent, cls) else parent
		node = cmds.parent(node, parent)

		return cls(node)

	def transform(self):
		if self._transform is None:
			matrix = cmds.xform(self._marker, q=True, matrix=True, worldSpace=True)
			self._transform = Matrix4(matrix).asTransform()
			self._translation = self._transform.translation

		return self._transform

	def translation(self):
		if self._translation is None:
			translation = cmds.xform(self._marker, q=True, translation=True, worldSpace=True)
			self._translation = Vector3(translation)

		return self._translation




