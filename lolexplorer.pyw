#!/usr/bin/env python
# as of now this is just a skeleton, don't trust anything
# Here be killer robot dragon assassins!
import tkinter as tk
import tkinter.messagebox
import raf

class LoLExplGUI(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.grid()
		self.createWidgets()

	def createWidgets(self):
		self.quitButton = tk.Button(self, text='Quit', command=self.quit)
		self.quitButton.grid(column=1)
		self.lelButton = tk.Button(self, text='lel', command=self.printlel)
		self.lelButton.grid(column=0, row=0)

	def printlel(self):
		tkinter.messagebox.showinfo(title='lel', message='wololololololoo')

root = LoLExplGUI()
root.master.title('LoL Explorer')
root.mainloop()
