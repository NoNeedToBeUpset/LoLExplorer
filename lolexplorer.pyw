#!/usr/bin/env python
# Here be killer robot dragon assassins!
# fuckin GUIs
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox

# my own imports
import preferences
import raf
import util

# this is how to define a menubar properly
# toplevel: List of (label, sublabels)-tuples
#	label: string
#	sublabels: (string, action)-tuples
menudef = [
	('File', [
		('Save', lambda:tkinter.messagebox.showinfo(title='hah, no', message='yeeaaaahhh..')),
		('SEPARATOR', None),
		('Exit', exit),
	]),
	('Edit', [
		('Preferences', lambda:PreferencesDialog().mainloop()),
	]),
	('Actions', [
		('Find archive files', lambda:(updateArchLst(), le.showArchLst())),
		('List archive files', lambda:le.showArchLst()),
	]),
	('Help', [
		('About', lambda:tkinter.messagebox.showinfo(
				title=preferences.about['title'],
				message=preferences.about['msg'])),
	]),
]

# cache the archives found in loldir
archlst = []

class ModifyFile(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.top = tk.Toplevel(master)
		self.top.title('Modify an individual file')
		self.top.geometry("300x100+50+50")

class LoLExplGUI(tk.Frame):
	def __init__(self, master=None, title='LoL Explorer'):
		tk.Frame.__init__(self, master)
		self.master.title(title)
		self.master.geometry("500x200+50+50")
		self.pack()

		# setup what is needed of our preferences
		preferences.path['loldir'][0] = util.guessLolDir()

		# create a menubar as defined in menudef
		self.menubar = tk.Menu(self, tearoff=0)
		for cmenu in menudef:
			cascade = tk.Menu(self.menubar, tearoff=0)
			self.menubar.add_cascade(label=cmenu[0], menu=cascade)
			for item in cmenu[1]:
				if item[0] == 'SEPARATOR':
					cascade.add_separator()
				else:
					cascade.add_command(label=item[0], command=item[1])

		# show menubar
		self.master.config(menu=self.menubar)

		# create a canvas where we do all our work
		self.workcanvas = tk.Canvas(self)
		self.workcanvas.pack()

		"""self.buttons = {
			'lel'		: tk.Button(self, text='toplel', command=self.printlel),
			'modfile'	: tk.Button(self, text='Modify a file', command=self.modfile),
			'preferences'	: tk.Button(self, text='Preferences', command=self.prefs),
		}

		for butt in sorted(self.buttons.keys()):
			self.buttons[butt].pack()"""

		self.welcomelabel = tk.Label(self.workcanvas, text="Welcome! Select something to do from the menu.")
		self.welcomelabel.pack(anchor='center')

	def modfile(self):
		mfw = ModifyFile(self)
		mfw.mainloop()

	def prefs(self):
		pref = PreferencesDialog()
		pref.mainloop()

	def printlel(self):
		tkinter.messagebox.showinfo(title='lel', message='wololololololoo')

	def showArchLst(self):
		tkinter.messagebox.showinfo(title='TODO', message='*list of archive files*')

class PreferencesDialog(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.top = tk.Toplevel(master)
		self.top.title("Preferences")
		self.top.geometry("400x600")

		# display the path preferences
		self.top.pathframe = tk.LabelFrame(self.top, text="Paths")
		self.top.pathframe.grid()
		self.path = {}
		for p in preferences.path.keys():
			self.path[p] = (
				tk.Label(self.top.pathframe, text=preferences.path[p][1]),
				tk.Entry(self.top.pathframe),
				tk.Button(self.top.pathframe, text='Browse',
					command=lambda key=p:self.browseForPath(key)))
			if preferences.path[p][0]:
				self.path[p][1].insert(0, preferences.path[p][0])

		cRow = 0
		for p in sorted(self.path.keys()):
			col = 0
			while col < 3:
				self.path[p][col].grid(row=cRow, column=col)
				col += 1
			cRow += 1

	def browseForPath(self, pathkey):
		# start browsing at the current path, if one is set
		newp = tkinter.filedialog.askdirectory(initialdir=self.path[pathkey][1].get())
		if newp != '':
			util.setEntry(self.path[pathkey][1], newp)
			preferences.path[pathkey][0] = newp

def updateArchLst():
	archlst = util.findAllRafsIn(preferences.path['loldir'][0])

root = tk.Tk()
le = LoLExplGUI(root)
le.mainloop()
