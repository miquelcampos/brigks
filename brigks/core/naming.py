
def getSystemKey(location, name):
	return "{name}_{location}".format(location=location, name=name)


def getObjectName(usage, location, name, part):
	return "{use}_{loc}_{name}_{part}".format(
								use=usage,
								loc=location,
								name=name,
								part=part)


def getMarkerName(self, part):
	return getObjectName()
	return "Gde_{loc}_{name}_{part}".format(
			loc=self.settings["location"],
			name=self.settings["name"],
			part=part)
