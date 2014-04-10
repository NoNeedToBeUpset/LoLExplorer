#!/usr/bin/env python
# contains miscellaneous utilities
import os
import tkinter as tk

# common directories for LoL to be installed in
loldirguesses = ["C:/Program Files (x86)/Riot Games/League of Legends",
		"C:/Program Files/Riot Games/League of Legends",
		"C:/Riot Games/League of Legends"]

# find any and all .raf-files located under path, return as a list
def findAllRafsIn(path):
	raffiles = []
	for dirname, dirnames, filenames in os.walk(path):
		for filename in filenames:
			if filename[-4:] == '.raf':
				raffiles.append(filename)
	return raffiles

# the first path in loldirguesses is assumed to contain LoL game files
def guessLolDir():
	for p in loldirguesses:
		if os.path.exists(p):
			return p

	return None

# set the value of a tk.Entry
def setEntry(self, ent, val):
	ent.delete(0, tk.END)
	ent.insert(0, val)