#!/usr/bin/env python
# see http://leagueoflegends.wikia.com/wiki/RAF:_Riot_Archive_File
# for details about the RAF-format
from ctypes import c_uint
import os, struct, sys, zlib

RAF_MAGIC = 0x18be0ef0

class RAF():
	def __init__(self, filename):
		# we store all our info in a hash ("dict", pyfags)
		self.fileinfo = {}

		# start off with the paths
		self.fileinfo['rafpath'] = filename
		self.fileinfo['rafdatpath'] = filename + ".dat"
		self.file = open(filename, "rb")
		self.datfile = None

		# make sure the magic number checks out
		self.fileinfo['magic'] = self.getULong()
		if self.fileinfo['magic'] != RAF_MAGIC:
			raise Exception('not a valid RAF-file, invalid magic number')

		# read and store the RAF-version of the file
		self.fileinfo['version'] = self.getULong()

		# managerindex is a value used internally by Riot that we are not allowed to modify :(
		self.fileinfo['managerindex'] = self.getULong()

		# offset to the file list
		self.fileinfo['filelistoffs'] = self.getULong()

		# offset to the path list
		self.fileinfo['pathlistoffs'] = self.getULong()

		# store file and path lists as... lists :o
		self.fileinfo['filelist'] = []
		self.fileinfo['pathlist'] = []

		# read the filelist, starting with the entrycount
		self.file.seek(self.fileinfo['filelistoffs'])
		self.fileinfo['filecount'] = self.getULong()

		# now that we know how many entries there are, read them all
		i = 0
		while i < self.fileinfo['filecount']:
			entry = {'pathhash': self.getULong()}
			entry['dataoffs'] = self.getULong()
			entry['datasz'] = self.getULong()
			entry['pathlistidx'] = self.getULong()
			self.fileinfo['filelist'].append(entry)
			i += 1

		# do the same as for files with paths
		self.file.seek(self.fileinfo['pathlistoffs'])
		self.fileinfo['pathlistsz'] = self.getULong()
		self.fileinfo['pathcount'] = self.getULong()
		i = 0
		while i < self.fileinfo['pathcount']:
			entry = {'pathoffs': self.getULong()}
			entry['pathlen'] = self.getULong()

			# save our current position in the file and read the path
			curpos = self.file.tell()
			self.file.seek(self.fileinfo['pathlistoffs'] + entry['pathoffs'])
			# -1 because null is included in pathlen
			entry['path'] = self.file.read(entry['pathlen'] - 1)
			entry['hash'] = self.hashString(entry['path'])
			
			# add info to pathlist, seek back and read another
			self.fileinfo['pathlist'].append(entry)
			self.file.seek(curpos)
			i += 1

	# dump the information to stdout, mainly for debugging and inspecting data during development
	def dump(self):
		keys = list(self.fileinfo.keys())
		keys.sort()
		for key in keys:
			if key == 'magic':
				print(key + ": " + hex(self.fileinfo[key]))
			elif key == 'pathlist' or key == 'filelist':
				print(key + ":")
				for e in self.fileinfo[key]:
					print("\t", e)
			else:
				print(key + ": " + str(self.fileinfo[key]))

	# extract the file specified in fileentry to basedir/path/to/file
	# fileentry is an arbitrary element from filelist
	def extract(self, fileentry, basedir="."):
		if not self.datfile:
			self.datfile = open(self.fileinfo['rafdatpath'], "rb")

		self.datfile.seek(fileentry['dataoffs'])
		path = self.fileinfo['pathlist'][fileentry['pathlistidx']]

		if not fileentry['pathhash'] == path['hash']:
			raise Exception('hashes do not match')

		# forget path entry since it is now validated
		path = path['path'].decode('utf-8')

		# create the directories needed, if they don't already exist
		os.makedirs(os.path.join(basedir, os.path.dirname(path)), exist_ok=True)

		# write file in one chunk
		with open(os.path.join(basedir, path), "wb") as fh:
			zdat = self.datfile.read(fileentry['datasz'])
			# try to decompress file with zlib, assume that it is not compressed if we get ANY error
			try:
				dat = zlib.decompress(zdat)
			except zlib.error as e:
				dat = zdat
			fh.write(dat)

	# extract all the files in the current .raf-file into basedir
	def extractAll(self, basedir=".", verbose=False):
		for e in self.fileinfo['filelist']:
			if verbose:
				print(self.fileinfo['pathlist'][e['pathlistidx']])
			self.extract(e, basedir)
	
	# reads 4 bytes from self.file and returns them interpreted as an unsigned int (32 bits)
	def getULong(self):
		return struct.unpack('<I', self.file.read(4))[0]

	# hashes bytes in s as per http://leagueoflegends.wikia.com/wiki/RAF:_Riot_Archive_File#Hash_Function
	# returns hash... duh
	def hashString(self, s):
		hash = 0
		temp = 0
		for c in s.lower():
			hash = (hash << 4) + c
			temp = hash & 0xf0000000
			if temp != 0:
				hash = hash ^ (temp >> 24)
				hash = hash ^ temp
		return hash

def main():
	raf = RAF(sys.argv[1])
	raf.dump()
	print("Searching for matching hashes...")
	hashmatches = 0
	for f in raf.fileinfo['filelist']:
		for p in raf.fileinfo['pathlist']:
			if p['hash'] == f['pathhash']:
				hashmatches += 1
	print("Found", hashmatches, "matches.")
	if hashmatches == raf.fileinfo['filecount']:
		print("Good, that's one match for every file.")
	else:
		print("Oh-oh, found", hashmatches, "matches but have", raf.fileinfo['filecount'], "files.")

if __name__ == '__main__':
	main()
