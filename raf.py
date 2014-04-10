#!/usr/bin/env python
# see http://leagueoflegends.wikia.com/wiki/RAF:_Riot_Archive_File
# for details about the RAF-format
from ctypes import c_uint
import os, struct, sys, zlib

RAF_MAGIC = 0x18be0ef0

class RAF():
	# data fields in RAF:
	# top level:
	# file		-	file handle to the opened .raf-file
	# datfile	-	^ .raf.dat, may be None if we haven't opened it yet
	# --- fileinfo[key]
	# key		-	desc
	# magic		-	magic number read from file, should always be RAF_MAGIC
	# version	-	version of the RAF archive
	# rafpath	-	path to the file.raf-archive
	# rafdatpath	-	^ .raf.dat
	# managerindex	-	some riot-internal value that we shouldn't modify
	# filelistoffs	-	offset in .raf to the file list
	# pathlistoffs	-	^ path list
	# filecount	-	amount of file-entries
	# pathcount	-	^ path-entries
	# pathlistsz	-	size if the entire path list
	# --- fileinfo['filelist']
	# pathhash	-	hash of the file's (archive-internal) path
	# dataoffs	-	offset in .raf.dat to this file's data
	# datasz	-	size of said data
	# pathlistidx	-	index into the path list of our path
	# --- fileinfo['pathlist']
	# pathoffs	-	offset _from_the_path_list_ of the path
	# pathlen	-	length of path (including null)
	# path		-	the path (extracted for our convenience
	# hash		-	hash (calculated by us)
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
		# TODO: fck shit up with a hex editor
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
		elif not self.datfile.readable():
			self.datfile.close()
			self.datfile = open(self.fileinfo['rafdatpath'], "rb")

		self.datfile.seek(fileentry['dataoffs'])
		path = self.fileinfo['pathlist'][fileentry['pathlistidx']]

		# if the hashes do not match... something is horribly wrong
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

	# path	  - /path/to/data/file
	# arcoath - archive internal path
	def updateFile(self, path, arcpath):
		# make sure we can both read and write
		if not (self.file.readable() and self.file.writable()):
			self.file.close()
			self.file = open(self.fileinfo['rafpath'], "r+b")

		# open, read and compress file data
		nfile = open(path, "rb")

		# read, compress, append to zdat, repeat
		zdat = b''
		zcompr = zlib.compressobj()
		while True:
			dat = nfile.read(4096)	# 4k blocks seems reasonable
			if not dat:
				break
			zdat += zcompr.compress(dat)

		# finalize compression, compressed file data is now in zdat
		zdat += zcompr.flush()

		# in case arcpath is a string, convert to bytes
		# if it is already bytes, nothing changes
		try:
			arcpath = arcpath.encode('utf-8')
		except AttributeError:
			pass

		# then we hash it
		aphash = self.hashString(arcpath)

		# find the corresponding entry
		fent = None
		for ent in self.fileinfo['filelist']:
			if ent['pathhash'] == aphash:
				fent = ent
				break

		# maybe TODO: call some addFile()-func instead
		if not fent:
			raise Exception("path not already in file, cannot update")

		# now find the data in the file
		# skip the entry count, we already know that
		self.file.seek(self.fileinfo['filelistoffs'] + 4)

		# search for a matching hash
		i = 0
		while i < self.fileinfo['filecount']:
			thash = self.getULong()
			if thash == aphash:
				break
			i += 1

		# we are now at fileentry.dataoffs
		# if the new data size is smaller than or equal to the old one, we can overwrite the old
		# data with the new, keep dataoffs intact and adjust datasz. this potentially leaves a gap
		# after end of current file and start of the next, which we can live with
		# if new datasz > old datasz, we append the new data to the end of rafdat
		if fent['datasz'] > len(zdat):
			df = open(self.fileinfo['rafdatpath'], "ab")
			newoffs = df.tell()
			df.write(zdat)
			df.close()
			self.file.write(struct.pack('<I', newoffs))
			self.file.write(struct.pack('<I', len(zdat)))
		else:
			df = open(self.fileinfo['rafdatpath'], "r+b")
			df.seek(fent['dataoffs'])
			df.write(zdat)
			df.close()
			# skip over dataoffs since we need not set it
			self.file.seek(4, SEEK_CUR)
			self.file.write(struct.pack('<I', len(zdat)))

		# now the file should be updated

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
