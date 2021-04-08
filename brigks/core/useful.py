from maya import cmds

from brigks.utils import constants

# ----------------------------------------------------------------------------------
# ATTRIBUTES
# ----------------------------------------------------------------------------------
def createHarmonic(name, slave, master, amplitude=1.0, decay=8.0, frequency=0.5, termination=0.0, amplitudeAxis=(1,1,1)):
	if not cmds.pluginInfo("harmonics", q=True,  loaded=True):
		cmds.loadPlugin("harmonics")
	hNode = cmds.createNode("harmonics", name=name)

	cmds.connectAttr(hNode+".output", slave+".translate")
	cmds.connectAttr(master+".wm", hNode+".input")
	cmds.connectAttr(master+".pim", hNode+".parentInverse")
	cmds.connectAttr("time1.o", hNode+".timeIn")

	cmds.setAttr(hNode+".update", True)
	cmds.setAttr(hNode+".amplitude", amplitude)
	cmds.setAttr(hNode+".axisAmp0", amplitudeAxis[0])
	cmds.setAttr(hNode+".axisAmp1", amplitudeAxis[1])
	cmds.setAttr(hNode+".axisAmp2", amplitudeAxis[2])
	cmds.setAttr(hNode+".decay", decay)
	cmds.setAttr(hNode+".frequencyMult", frequency)
	cmds.setAttr(hNode+".termination", termination)

