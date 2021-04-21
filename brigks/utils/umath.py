from copy import copy

from math3d.transformation import Transformation, TransformationArray
from math3d.vectorN import Vector3



def createTransform(t=None, r=None, s=None):
	return Transformation.fromParts(translation=t, rotation=r, scale=s)


def upVector(posA, posB, normal, ratio, negate=False):
	n = copy(normal)
	if negate:
		n *= -1
	
	pos = posB - posA
	length = pos.length()
	pos = n.cross(pos)
	pos.normalize()

	pos *= length

	pos += posA.lerp(posB, ratio)

	return pos 