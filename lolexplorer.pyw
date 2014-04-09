#!/usr/bin/env python
# as of now this is just a skeleton, don't trust anything
# Here be killer robot dragon assassins!
import tkinter as tk
import raf

class LoLExplGUI(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.grid()
		self.createWidgets()

	def createWidgets(self):
		self.quitButton = tk.Button(self, text='Quit', command=self.quit)
		self.quitButton.grid()
		self.lelButton = tk.Button(self, text='lel', command=self.printlel)
		self.lelButton.grid()

	def printlel(self):
		print("lel")

root = LoLExplGUI()
root.master.title('LoL Explorer')
root.mainloop()
