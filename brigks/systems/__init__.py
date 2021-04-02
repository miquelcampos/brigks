import os


def getSystemGuideClass(systemType, version=None):
	return _getClass(systemType, "guide", "SystemGuide", version)

def getSystemBuilderClass(systemType, version=None):
	return _getClass(systemType, "builder", "SystemBuilder", version)

def getSystemWidgetClass(systemType, version=None):
	return _getClass(systemType, "widget", "SystemWidget", version)

def _getClass(systemType, moduleName, classSuffix, version=None):
	#TODO Implement version. Requires moving code in v001 folder for each system
	# Get Module
	moduleName = ".".join(["brigks", "systems", systemType, moduleName])
	module = __import__(moduleName, globals(), locals(), ["*"], -1)

	# Get Class
	className = systemType.title()+classSuffix
	try:
		Class = getattr(module, className)
	except AttributeError:
		msg = "'{m}' object has no attribute '{c}'".format(m=moduleName, c=className)
		raise AttributeError(msg)

	return Class


def getSystemList():
	folder = os.path.dirname(__file__)
	for root, dirs, files in os.walk(folder, topdown=True):
	   	return sorted(dirs)