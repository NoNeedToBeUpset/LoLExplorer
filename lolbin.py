#!/usr/bin/env python
# this will, Soon(tm), not be broken and actually work quite well
class Inibin():
	def __init__(self, binfile):
		with open(binfile, "rb") as fh:
			self.version = struct.unpack('B', fh.read(1))
			if self.version != 2:	# we only support version 2
				raise Exception("invalid inibin-version")
			
		return

class Troybin():
	def __init__(self, binfile):
		return

