
from brigks import config

# ----------------------------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------------------------
def getSystemKey(location, name):
	return "{name}_{location}".format(location=location, name=name)


def getObjectName(use, location, name, part):
	return config.TOKENS.format(
					use=use,
					loc=location,
					name=name,
					part=part)


# def getMarkerName(self, part):
# 	return getObjectName()
# 	return "Gde_{loc}_{name}_{part}".format(
# 			loc=self.settings["location"],
# 			name=self.settings["name"],
# 			part=part)
