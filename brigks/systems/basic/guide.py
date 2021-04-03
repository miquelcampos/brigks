from maya import cmds

from brigks.systems.systemGuide import SystemGuide
from math3d.vectorN import Vector3

class BasicSystemGuide(SystemGuide):	

	markerNames = ("Part",)
	markerMinMax = dict(
		Part=(1,-1),
		)
	defaultPositions = dict(
		Part1=Vector3([0,1,0]),
		)

	def addSettings(self):
		self.settings["addControllers"] = True
		self.settings["useIkColor"] = False

		self.settings["tx"] = True
		self.settings["ty"] = True
		self.settings["tz"] = True
		self.settings["rx"] = True
		self.settings["ry"] = True
		self.settings["rz"] = True
		self.settings["sx"] = True
		self.settings["sy"] = True
		self.settings["sz"] = True
		
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
			ports[port] = ["slotParent", "meshAttach", "nurbsParent", "multiParent", "customParent"]

		ports["UI"] = ["uiHost"]

		return ports

	def connectionSlots(self):
		super(BasicSystemGuide, self).connectionSlots()

		slots = {}
		for marker in self.markers.keys():
			slot = marker.split("_")[-1]
			slots[slot] = ("Ctl", slot)

		return slots

		