from maya import cmds

from tools.marbie.systems.systemGuide import SystemGuide

class BasicSystemGuide(SystemGuide):	

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(1,-1)
		)

	def addSettings(self):
		self.settings["addControllers"] = True
		self.settings["useIkColor"] = False

		self.settings["posx"] = True
		self.settings["posy"] = True
		self.settings["posz"] = True
		self.settings["rotx"] = True
		self.settings["roty"] = True
		self.settings["rotz"] = True
		self.settings["sclx"] = True
		self.settings["scly"] = True
		self.settings["sclz"] = True
		
		self.settings["rotorder"] = True
		self.settings["defaultRotationOrder"] = "XYZ"

		self.settings["splitRotation"] = False
		
		self.settings["dynamic"] = False
		self.settings["dynActive"] = False
		self.settings["amplitude"] = 1.0

		self.settings["amplitudeX"] = 1.0
		self.settings["amplitudeY"] = 1.0
		self.settings["amplitudeZ"] = 1.0
		self.settings["decay"] = 8.0
		self.settings["frequency"] = .25
		self.settings["termination"] = 0.0

		self.settings["dynamicAnimatable"] = False

	def connectionPorts(self):
		super(BasicSystemGuide, self).connectionPorts()
		
		ports = {}
		for marker in self.markers.keys():
			port = marker.split("_")[-1]
			ports[port] = ["parent", "attachToGeo", "multi", "customParent"]

		ports["UI"] = ["parent"]

		return ports

	def connectionSlots(self):
		super(BasicSystemGuide, self).connectionSlots()

		slots = {}
		for marker in self.markers.keys():
			slot = marker.split("_")[-1]
			slots[slot] = ("Ctl", slot)

		return slots

		