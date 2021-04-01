from maya import cmds

# TODO: Replace with new math3D linbray
from cross3d.xmathutils import Transform, Matrix, Vector
from math3d import Transformation, Matrix4, Vector3

def checkMarkersMinMax(markers, markerNames, markerMinMax):
	# This method checks that all the mandatory markers exist
	# It return the name of the marker and the object from the dictionary if it is found
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

	@classmethod #TODO can we have the marker creation here
	def create(cls, name, parent, matrix=None):
		node = cmds.spaceLocator(name=name)
		if matrix:
			cmds.xform(node, matrix=matrix, worldSpace=True)
		parent = parent._marker if isinstance(parent, cls) else parent
		node = cmds.parent(node, parent)

		return cls(node)

	def transform(self):
		if not self._transform:
			matrix = cmds.xform(self._marker, q=True, matrix=True, worldSpace=True)
		# 	matrix = [matrix[i*4:i*4+4] for i in range(4)]
		# 	matrix = Matrix(matrix)
		# 	self._transform = Transform.Matrix(matrix)
		# 	self._translation = self._transform.translation
			matrix = Matrix4(matrix)
			self._transform = Transformation(matrix)
			self._translation = self._transform.translation

		return self._transform

	def translation(self):
		if not self._translation:
			translation = cmds.xform(self._marker, q=True, translation=True, worldSpace=True)
			# self._translation = Vector(translation)
			self._translation = Vector3(translation)

		return self._translation




