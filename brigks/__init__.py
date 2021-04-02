
# from brigks.core.guide import Guide
# from brigks.core.builder import Builder


import sys
math3d = r"\\source\source\dev\passerin\math3d"
print math3d
if math3d not in sys.path:
	sys.path.append(math3d)


from brigks.core.guide import Guide
from brigks.core.builder import Builder 