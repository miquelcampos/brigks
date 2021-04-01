


def getSystemConnectionClass(connectionType):
	return _getClass(connectionType, "connection", "SystemConnection")

def getConnectionWidgetClass(connectionType):
	return _getClass(connectionType, "widget", "ConnectionWidget")

def _getClass(connectionType, moduleName, classSuffix):
	# Get Module
	moduleName = ".".join(["tools", "marbie", "connections", connectionType, moduleName])	
	module = __import__(moduleName, globals(), locals(), ["*"], -1)

	className = connectionType.title()+classSuffix
	Class = getattr(module, className)

	return Class