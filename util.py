#!/usr/bin/env python
import os
# contains miscellaneous utility functions

# find any and all .raf-files located under path, return as a list
def findAllRafsIn(path):
	raffiles = []
	for dirname, dirnames, filenames in os.walk(path):
		for filename in filenames:
			file = os.path.join(dirname, filename)
			if file[-4:] == '.raf':
				raffiles.append(file)
	return raffiles
