
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