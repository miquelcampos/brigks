import os


def getSystemGuideClass(systemType):
	return _getClass(systemType, "guide", "SystemGuide")

def getSystemBuilderClass(systemType):
	return _getClass(systemType, "widget", "SystemBuilder")

def getSystemWidgetClass(systemType):
	return _getClass(systemType, "widget", "SystemWidget")

def _getClass(systemType, moduleName, classSuffix):
	# Get Module
	moduleName = ".".join(["tools", "marbie", "systems", systemType, moduleName])
	module = __import__(moduleName, globals(), locals(), ["*"], -1)

	# Get Class
	className = systemType.title()+classSuffix
	Class = getattr(module, className)

	return Class


def getSystemList():
	folder = os.path.dirname(__file__)
	for root, dirs, files in os.walk(folder, topdown=True):
	   	return sorted(dirs)