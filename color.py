
def hexToRGB(value):
	"""
	Parses a hex color string (with or without #)
	and returns a tuple with 0-255 values
	"""
	value = value.lstrip('#')
	lv = len(value)
	return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
